from __future__ import annotations

import logging
import os
import tempfile
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import CTerm, cterm_symbolic
from pyk.kast.inner import KApply, KSequence, KSort, KToken, KVariable, Subst
from pyk.kast.manip import abstract_term_safely, build_rule, free_vars, split_config_from
from pyk.kast.outer import KDefinition, KFlatModule, KImport, KRequire
from pyk.kast.prelude.collections import list_empty, list_of, map_of
from pyk.kast.prelude.kint import intToken
from pyk.kast.prelude.utils import token
from pyk.kcfg import KCFG
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
from pyk.kcfg.show import NodePrinter
from pyk.ktool.kompile import LLVMKompileType, PykBackend, kompile
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun
from pyk.proof.reachability import APRProof, APRProver
from pyk.proof.show import APRProofNodePrinter

from .build import HASKELL_DEF_DIR, KMIR_SOURCE_DIR
from .cargo import cargo_get_smir_json
from .kast import mk_call_terminator, symbolic_locals
from .kdist.plugin import _default_args
from .kparse import KParse
from .parse.parser import Parser
from .smir import SMIRInfo

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from typing import Any, Final

    from pyk.cterm.show import CTermShow
    from pyk.kast.inner import KInner
    from pyk.kore.syntax import Pattern
    from pyk.utils import BugReport

    from .options import DisplayOpts, ProveRSOpts

_LOGGER: Final = logging.getLogger(__name__)


class KMIR(KProve, KRun, KParse):
    llvm_library_dir: Path | None
    bug_report: BugReport | None

    def __init__(
        self, definition_dir: Path, llvm_library_dir: Path | None = None, bug_report: Path | None = None
    ) -> None:
        self.bug_report = bug_report_arg(bug_report) if bug_report is not None else None
        KProve.__init__(self, definition_dir, bug_report=self.bug_report)
        KRun.__init__(self, definition_dir, bug_report=self.bug_report)
        KParse.__init__(self, definition_dir)
        self.llvm_library_dir = llvm_library_dir

    @staticmethod
    def from_kompiled_program(smir_info: SMIRInfo, bug_report: Path | None = None) -> KMIR:
        kmir = KMIR(HASKELL_DEF_DIR)

        prog_module = kmir.make_program_module(smir_info)

        with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as prog_mod_file:
            prog_mod_file.write(kmir.pretty_print(prog_module))
        _LOGGER.info(f'Program module written to {prog_mod_file.name}')

        # kompile the module, for Haskell and for LLVM-library
        # code using KompileTarget from kmir.kdist.plugin
        llvm_args = {
            'main_file': prog_mod_file.name,
            'main_module': prog_module.main_module_name,
            'backend': PykBackend.LLVM,
            'llvm_kompile_type': LLVMKompileType.C,
            'md_selector': 'k & ! symbolic',
            **_default_args(KMIR_SOURCE_DIR / 'mir-semantics'),
        }
        llvm_out = kompile(output_dir='out/llvm', verbose=True, **llvm_args)

        hs_args = {
            'main_file': prog_mod_file.name,
            'main_module': prog_module.main_module_name,
            'backend': PykBackend.HASKELL,
            'md_selector': 'k & ! concrete',
            **_default_args(KMIR_SOURCE_DIR / 'mir-semantics'),
        }
        hs_out = kompile(output_dir='out/hs/', verbose=True, **hs_args)

        _LOGGER.info(f'Kompile output: LLVM: {llvm_out},HS:   {hs_out}')

        if os.path.exists(prog_mod_file.name):
            os.remove(prog_mod_file.name)

        # make a new KMIR with these paths
        return KMIR(hs_out, llvm_out, bug_report=bug_report)

    class Symbols:
        END_PROGRAM: Final = KApply('#EndProgram_KMIR-CONTROL-FLOW_KItem')

    @cached_property
    def parser(self) -> Parser:
        return Parser(self.definition)

    @contextmanager
    def kcfg_explore(self, label: str | None = None) -> Iterator[KCFGExplore]:
        with cterm_symbolic(
            self.definition,
            self.definition_dir,
            llvm_definition_dir=self.llvm_library_dir,
            bug_report=self.bug_report,
            id=label if self.bug_report is not None else None,  # NB bug report arg.s must be coherent
            interim_simplification=50,  # working around memory problems in LLVM backend calls
        ) as cts:
            yield KCFGExplore(cts, kcfg_semantics=KMIRSemantics())

    def functions(self, smir_info: SMIRInfo) -> dict[int, KInner]:
        functions: dict[int, KInner] = {}

        # Parse regular functions
        for item_name, item in smir_info.items.items():
            if not item_name in smir_info.function_symbols_reverse:
                _LOGGER.warning(f'Item not found in SMIR: {item_name}')
                continue
            parsed_item = self.parser.parse_mir_json(item, 'MonoItem')
            if not parsed_item:
                raise ValueError(f'Could not parse MonoItemKind: {parsed_item}')
            parsed_item_kinner, _ = parsed_item
            assert isinstance(parsed_item_kinner, KApply) and parsed_item_kinner.label.name == 'monoItemWrapper'
            # each item can have several entries in the function table for linked SMIR JSON
            for ty in smir_info.function_symbols_reverse[item_name]:
                functions[ty] = parsed_item_kinner.args[1]

        # Add intrinsic functions
        for ty, sym in smir_info.function_symbols.items():
            if 'IntrinsicSym' in sym and ty not in functions:
                functions[ty] = KApply(
                    'IntrinsicFunction',
                    [KApply('symbol(_)_LIB_Symbol_String', [token(sym['IntrinsicSym'])])],
                )

        return functions

    def make_program_module(self, smir_info: SMIRInfo) -> KDefinition:
        equations = []

        for fty, kind in self.functions(smir_info).items():
            rule, _ = build_rule(
                f'lookupFunction-{fty}',
                KApply('lookupFunction', (KApply('ty', (token(fty),)),)),
                kind,
            )
            equations.append(rule)

        parser = Parser(self.definition)
        types: set[KInner] = set()
        for type in smir_info._smir['types']:
            parse_result = parser.parse_mir_json(type, 'TypeMapping')
            assert parse_result is not None
            type_mapping, _ = parse_result
            assert isinstance(type_mapping, KApply) and len(type_mapping.args) == 2
            ty, tyinfo = type_mapping.args
            if ty in types:
                raise ValueError(f'Key collision in type map: {ty}')
            types.add(ty)
            assert isinstance(ty, KApply) and len(ty.args) == 1 and isinstance(ty.args[0], KToken)
            rule, _ = build_rule(
                f'lookupTy-{ty.args[0].token}',
                KApply('lookupTy', (ty,)),
                tyinfo,
            )
            equations.append(rule)

        for alloc in smir_info._smir['allocs']:
            alloc_id, value = self._decode_alloc(smir_info=smir_info, raw_alloc=alloc)
            assert isinstance(alloc_id, KApply) and isinstance(alloc_id.args[0], KToken)
            rule, _ = build_rule(
                f'lookupAlloc-{alloc_id.args[0].token}',
                alloc_id,
                value,
            )
            equations.append(rule)

        name = smir_info.name.replace('_', '-')

        module = KFlatModule(f'KMIR-PROGRAM-{name}', equations, (KImport('KMIR'),))

        return KDefinition(f'KMIR-PROGRAM-{name}', (module,), (KRequire('kmir.md'),))

    def make_call_config(
        self,
        smir_info: SMIRInfo,
        *,
        start_symbol: str = 'main',
        sort: str = 'GeneratedTopCell',
        init: bool = False,
    ) -> tuple[KInner, list[KInner]]:
        if not start_symbol in smir_info.function_tys:
            raise KeyError(f'{start_symbol} not found in program')

        args_info = smir_info.function_arguments[start_symbol]
        locals, constraints = symbolic_locals(smir_info, args_info)
        types = self._make_type_map(smir_info)

        _subst = {
            'K_CELL': mk_call_terminator(smir_info.function_tys[start_symbol], len(args_info)),
            'STARTSYMBOL_CELL': KApply('symbol(_)_LIB_Symbol_String', (token(start_symbol),)),
            'STACK_CELL': list_empty(),  # FIXME see #560, problems matching a symbolic stack
            'LOCALS_CELL': list_of(locals),
            'MEMORY_CELL': self._make_memory_map(smir_info, types),
            'FUNCTIONS_CELL': self._make_function_map(smir_info),
            'TYPES_CELL': types,
        }

        _init_subst: dict[str, KInner] = {}
        if init:
            _subst['LOCALS_CELL'] = list_empty()
            init_config = self.definition.init_config(KSort(sort))
            _, _init_subst = split_config_from(init_config)

        for key in _init_subst:
            if key not in _subst:
                _subst[key] = _init_subst[key]

        subst = Subst(_subst)
        config = self.definition.empty_config(KSort(sort))
        return (subst.apply(config), constraints)

    def _make_memory_map(self, smir_info: SMIRInfo, types: KInner) -> KInner:
        raw_allocs = smir_info._smir['allocs']
        return map_of(
            self._decode_alloc(
                smir_info=smir_info,
                raw_alloc=raw_alloc,
            )
            for raw_alloc in raw_allocs
        )

    def _decode_alloc(self, smir_info: SMIRInfo, raw_alloc: Any) -> tuple[KInner, KInner]:
        from .decoding import UnableToDecodeValue, decode_alloc_or_unable

        alloc_id = raw_alloc['alloc_id']
        alloc_info = smir_info.allocs[alloc_id]
        value = decode_alloc_or_unable(alloc_info=alloc_info, types=smir_info.types)

        match value:
            case UnableToDecodeValue(msg):
                _LOGGER.debug(f'Decoding failed: {msg}')
            case _:
                pass

        alloc_id_term = KApply('allocId', intToken(alloc_id))
        return alloc_id_term, value.to_kast()

    def _make_function_map(self, smir_info: SMIRInfo) -> KInner:
        parsed_terms: dict[KInner, KInner] = {}
        for ty, body in self.functions(smir_info).items():
            parsed_terms[KApply('ty', [token(ty)])] = body
        return map_of(parsed_terms)

    def _make_type_map(self, smir_info: SMIRInfo) -> KInner:
        types: dict[KInner, KInner] = {}
        for type in smir_info._smir['types']:
            parse_result = self.parser.parse_mir_json(type, 'TypeMapping')
            assert parse_result is not None
            type_mapping, _ = parse_result
            assert isinstance(type_mapping, KApply) and len(type_mapping.args) == 2
            ty, tyinfo = type_mapping.args
            if ty in types:
                raise ValueError(f'Key collision in type map: {ty}')
            types[ty] = tyinfo
        return map_of(types)

    def run_smir(self, smir_info: SMIRInfo, start_symbol: str = 'main', depth: int | None = None) -> Pattern:
        smir_info = smir_info.reduce_to(start_symbol)
        init_config, init_constraints = self.make_call_config(smir_info, start_symbol=start_symbol, init=True)
        if len(free_vars(init_config)) > 0 or len(init_constraints) > 0:
            raise ValueError(f'Cannot run function with variables: {start_symbol} - {free_vars(init_config)}')
        init_kore = self.kast_to_kore(init_config, KSort('GeneratedTopCell'))
        result = self.run_pattern(init_kore, depth=depth)
        return result

    def apr_proof_from_smir(
        self,
        id: str,
        smir_info: SMIRInfo,
        start_symbol: str = 'main',
        sort: str = 'GeneratedTopCell',
        proof_dir: Path | None = None,
    ) -> APRProof:
        lhs_config, constraints = self.make_call_config(smir_info, start_symbol=start_symbol, sort=sort)
        lhs = CTerm(lhs_config, constraints)

        var_config, var_subst = split_config_from(lhs_config)
        _rhs_subst: dict[str, KInner] = {
            v_name: abstract_term_safely(KVariable('_'), base_name=v_name) for v_name in var_subst
        }
        _rhs_subst['K_CELL'] = KSequence([KMIR.Symbols.END_PROGRAM])
        rhs = CTerm(Subst(_rhs_subst)(var_config))
        kcfg = KCFG()
        init_node = kcfg.create_node(lhs)
        target_node = kcfg.create_node(rhs)
        return APRProof(id, kcfg, [], init_node.id, target_node.id, {}, proof_dir=proof_dir)

    def prove_rs(self, opts: ProveRSOpts) -> APRProof:
        if not opts.rs_file.is_file():
            raise ValueError(f'Rust spec file does not exist: {opts.rs_file}')

        label = str(opts.rs_file.stem) + '.' + opts.start_symbol
        if not opts.reload and opts.proof_dir is not None and APRProof.proof_data_exists(label, opts.proof_dir):
            _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {label}')
            apr_proof = APRProof.read_proof_data(opts.proof_dir, label)
        else:
            _LOGGER.info(f'Constructing initial proof: {label}')
            if opts.smir:
                smir_info = SMIRInfo.from_file(opts.rs_file)
            else:
                smir_info = SMIRInfo(cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir))

            smir_info = smir_info.reduce_to(opts.start_symbol)

            _LOGGER.info(f'Reduced items table size {len(smir_info.items)}')
            apr_proof = self.apr_proof_from_smir(
                label, smir_info, start_symbol=opts.start_symbol, proof_dir=opts.proof_dir
            )
            if apr_proof.proof_dir is not None and (apr_proof.proof_dir / apr_proof.id).is_dir():
                smir_info.dump(apr_proof.proof_dir / apr_proof.id / 'smir.json')
        if apr_proof.passed:
            return apr_proof
        with self.kcfg_explore(label) as kcfg_explore:
            prover = APRProver(kcfg_explore, execute_depth=opts.max_depth)
            prover.advance_proof(apr_proof, max_iterations=opts.max_iterations)
            return apr_proof


class KMIRSemantics(DefaultSemantics):
    def is_terminal(self, cterm: CTerm) -> bool:
        k_cell = cterm.cell('K_CELL')
        # <k> #EndProgram </k>
        if k_cell == KMIR.Symbols.END_PROGRAM:
            return True
        elif type(k_cell) is KSequence:
            # <k> #EndProgram ~> .K </k>
            if k_cell.arity == 1 and k_cell[0] == KMIR.Symbols.END_PROGRAM:
                return True
        return False


class KMIRNodePrinter(NodePrinter):
    def __init__(self, cterm_show: CTermShow, full_printer: bool = False) -> None:
        NodePrinter.__init__(self, cterm_show, full_printer=full_printer)


class KMIRAPRNodePrinter(KMIRNodePrinter, APRProofNodePrinter):
    smir_info: SMIRInfo | None

    def __init__(self, cterm_show: CTermShow, proof: APRProof, opts: DisplayOpts) -> None:
        KMIRNodePrinter.__init__(self, cterm_show, full_printer=opts.full_printer)
        APRProofNodePrinter.__init__(self, proof, cterm_show, full_printer=opts.full_printer)
        self.smir_info = None
        if opts.smir_info:
            self.smir_info = SMIRInfo.from_file(opts.smir_info)
        elif (
            proof.proof_dir is not None
            and (proof.proof_dir / proof.id).is_dir()
            and (proof.proof_dir / proof.id / 'smir.json').is_file()
        ):
            self.smir_info = SMIRInfo.from_file(proof.proof_dir / proof.id / 'smir.json')

    def _span(self, node: KCFG.Node) -> str | None:
        curr_span: int | None = None
        span_worklist: list[KInner] = [node.cterm.cell('K_CELL')]
        while span_worklist:
            next_item = span_worklist.pop(0)
            if type(next_item) is KApply:
                if (
                    next_item.label.name == 'span'
                    and type(next_item.args[0]) is KToken
                    and next_item.args[0].sort.name == 'Int'
                ):
                    curr_span = int(next_item.args[0].token)
                    break
                span_worklist = list(next_item.args) + span_worklist
            if type(next_item) is KSequence:
                span_worklist = list(next_item.items) + span_worklist
        if self.smir_info is not None and curr_span is not None and curr_span in self.smir_info.spans:
            path, start_row, _start_column, _end_row, _end_column = self.smir_info.spans[curr_span]
            return f'{str(path)[-30:]}:{start_row}'
        if curr_span is not None:
            return f'{curr_span}'
        return None

    def _function_name(self, node: KCFG.Node) -> str | None:
        curr_func_ty_kast = node.cterm.cell('CURRENTFUNC_CELL')
        if (
            type(curr_func_ty_kast) is KApply
            and curr_func_ty_kast.label.name == 'ty'
            and type(curr_func_ty_kast.args[0]) is KToken
            and curr_func_ty_kast.args[0].sort.name
        ):
            curr_func_ty = int(curr_func_ty_kast.args[0].token)
            if curr_func_ty == -1:
                return 'main'
            if self.smir_info is not None:
                if curr_func_ty in self.smir_info.function_symbols:
                    _sym = self.smir_info.function_symbols[curr_func_ty]
                    if 'NormalSym' in _sym:
                        sym = _sym['NormalSym']
                        if sym in self.smir_info.items:
                            name = self.smir_info.items[sym]['mono_item_kind']['MonoItemFn']['name']
                            assert type(name) is str
                            return name
        return None

    def print_node(self, kcfg: KCFG, node: KCFG.Node) -> list[str]:
        ret_strs = super().print_node(kcfg, node)
        ret_strs.append(self.cterm_show._printer(node.cterm.cell('K_CELL'))[0:80])
        curr_func = self._function_name(node)
        if curr_func is not None:
            ret_strs.append(f'function: {curr_func}')
        curr_span = self._span(node)
        if curr_span is not None:
            ret_strs.append(f'span: {curr_span}')
        return ret_strs
