from __future__ import annotations

import json
import logging
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply, KSort, KToken, KVariable
from pyk.kast.prelude.kint import intToken
from pyk.kast.prelude.string import stringToken
from pyk.kdist import kdist
from pyk.kore.syntax import App, EVar, SortApp, String, Symbol, SymbolDecl

from .kmir import KMIR

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path
    from typing import Any, Final

    from pyk.kast.inner import KInner
    from pyk.kore.syntax import Axiom, Pattern, Sentence

    from .smir import SMIRInfo


_LOGGER: Final = logging.getLogger(__name__)


class KompiledSMIR(ABC):
    @abstractmethod
    def create_kmir(self, *, bug_report_file: Path | None = None) -> KMIR: ...


@dataclass
class KompiledSymbolic(KompiledSMIR):
    haskell_dir: Path
    llvm_lib_dir: Path

    def create_kmir(self, *, bug_report_file: Path | None = None) -> KMIR:
        return KMIR(
            definition_dir=self.haskell_dir,
            llvm_library_dir=self.llvm_lib_dir,
            bug_report=bug_report_file,
        )


@dataclass
class KompiledConcrete(KompiledSMIR):
    llvm_dir: Path

    def create_kmir(self, *, bug_report_file: Path | None = None) -> KMIR:
        return KMIR(
            definition_dir=self.llvm_dir,
            bug_report=bug_report_file,
        )


@dataclass
class KompileDigest:
    digest: str
    symbolic: bool
    llvm_target: str
    llvm_lib_target: str
    haskell_target: str

    @staticmethod
    def load(target_dir: Path) -> KompileDigest:
        digest_file = KompileDigest._digest_file(target_dir)

        if not digest_file.exists():
            raise ValueError(f'Digest file does not exist: {digest_file}')

        data = json.loads(digest_file.read_text())
        return KompileDigest(
            digest=data['digest'],
            symbolic=data['symbolic'],
            llvm_target=data['llvm-target'],
            llvm_lib_target=data['llvm-lib-target'],
            haskell_target=data['haskell-target'],
        )

    def write(self, target_dir: Path) -> None:
        self._digest_file(target_dir).write_text(
            json.dumps(
                {
                    'digest': self.digest,
                    'symbolic': self.symbolic,
                    'llvm-target': self.llvm_target,
                    'llvm-lib-target': self.llvm_lib_target,
                    'haskell-target': self.haskell_target,
                },
            ),
        )

    @staticmethod
    def _digest_file(target_dir: Path) -> Path:
        return target_dir / 'smir-digest.json'


def _collect_evars(pattern: 'Pattern') -> set[EVar]:
    """Collect all EVar instances from a Kore pattern."""
    from pyk.kore.syntax import EVar

    evars: set[EVar] = set()

    def collect_evar(p: 'Pattern') -> None:
        if isinstance(p, EVar):
            evars.add(p)

    pattern.collect(collect_evar)
    return evars


def _add_exists_quantifiers(axiom: 'Axiom') -> 'Axiom':
    """Add \\exists quantifiers for variables that appear in RHS but not in LHS.

    For rewrite rules of the form:
        axiom{} \\rewrites{Sort}(LHS, RHS)

    This function finds variables in RHS that don't appear in LHS (existential variables)
    and wraps the RHS with \\exists quantifiers for those variables:
        axiom{} \\rewrites{Sort}(LHS, \\exists{Sort}(Var1, \\exists{Sort}(Var2, RHS)))
    """
    from pyk.kore.syntax import Axiom, Exists, Rewrites

    pattern = axiom.pattern

    # Only process rewrite rules
    if not isinstance(pattern, Rewrites):
        return axiom

    lhs = pattern.left
    rhs = pattern.right
    sort = pattern.sort

    # Collect variables from LHS and RHS
    lhs_vars = _collect_evars(lhs)
    rhs_vars = _collect_evars(rhs)

    # Find existential variables (in RHS but not in LHS)
    existential_vars = rhs_vars - lhs_vars

    if not existential_vars:
        return axiom

    _LOGGER.debug(f'Adding \\exists for {len(existential_vars)} variables: {[v.name for v in existential_vars]}')

    # Wrap RHS with \exists for each existential variable
    new_rhs = rhs
    for evar in sorted(existential_vars, key=lambda v: v.name):  # Sort for deterministic output
        new_rhs = Exists(sort=sort, var=evar, pattern=new_rhs)

    # Create new rewrite with wrapped RHS
    new_pattern = Rewrites(sort=sort, left=lhs, right=new_rhs)

    return Axiom(vars=axiom.vars, pattern=new_pattern, attrs=axiom.attrs)


def _load_extra_module_rules(kmir: KMIR, module_path: Path) -> list[Sentence]:
    """Load a K module from JSON and convert rules to Kore axioms.

    Args:
        kmir: KMIR instance with the definition
        module_path: Path to JSON module file (from --to-module output.json)

    Returns:
        List of Kore axioms converted from the module rules
    """
    from pyk.kast.outer import KFlatModule, KRule
    from pyk.konvert import krule_to_kore

    _LOGGER.info(f'Loading extra module rules: {module_path}')

    if module_path.suffix != '.json':
        _LOGGER.warning(f'Only JSON format is supported for --add-module: {module_path}')
        return []

    module_dict = json.loads(module_path.read_text())
    k_module = KFlatModule.from_dict(module_dict)

    axioms: list[Sentence] = []
    for sentence in k_module.sentences:
        if isinstance(sentence, KRule):
            try:
                axiom = krule_to_kore(kmir.definition, sentence)
                # Add \exists quantifiers for existential variables
                axiom = _add_exists_quantifiers(axiom)
                axioms.append(axiom)
            except Exception:
                _LOGGER.warning(f'Failed to convert rule to Kore: {sentence}', exc_info=True)

    return axioms


def kompile_smir(
    smir_info: SMIRInfo,
    target_dir: Path,
    *,
    bug_report: Path | None = None,
    extra_module: Path | None = None,
    symbolic: bool = True,
    llvm_target: str | None = None,
    llvm_lib_target: str | None = None,
    haskell_target: str | None = None,
) -> KompiledSMIR:
    kompile_digest: KompileDigest | None = None
    try:
        kompile_digest = KompileDigest.load(target_dir)
    except Exception:
        pass

    llvm_target = llvm_target or 'mir-semantics.llvm'
    llvm_lib_target = llvm_lib_target or 'mir-semantics.llvm-library'
    haskell_target = haskell_target or 'mir-semantics.haskell'

    expected_digest = KompileDigest(
        digest=smir_info.digest,
        symbolic=symbolic,
        llvm_target=llvm_target,
        llvm_lib_target=llvm_lib_target,
        haskell_target=haskell_target,
    )

    target_hs_path = target_dir / 'haskell'
    target_llvm_lib_path = target_dir / 'llvm-library'
    target_llvm_path = target_dir / 'llvm'

    if kompile_digest == expected_digest:
        _LOGGER.info(f'Kompiled SMIR up-to-date, no kompilation necessary: {target_dir}')
        if symbolic:
            return KompiledSymbolic(haskell_dir=target_hs_path, llvm_lib_dir=target_llvm_lib_path)
        else:
            return KompiledConcrete(llvm_dir=target_llvm_path)

    _LOGGER.info(f'Kompiling SMIR program: {target_dir}')

    kompile_digest = expected_digest
    target_dir.mkdir(parents=True, exist_ok=True)

    haskell_def_dir = kdist.which(haskell_target)
    kmir = KMIR(haskell_def_dir)
    smir_rules: list[Sentence] = list(make_kore_rules(kmir, smir_info))
    _LOGGER.info(f'Generated {len(smir_rules)} function equations to add to `definition.kore')

    # Load and convert extra module rules if provided
    # These are kept separate because LLVM backend doesn't support configuration rewrites
    extra_rules: list[Sentence] = []
    if extra_module is not None:
        extra_rules = _load_extra_module_rules(kmir, extra_module)
        _LOGGER.info(f'Added {len(extra_rules)} rules from extra module: {extra_module}')

    # Combined rules for Haskell backend (supports both function equations and rewrites)
    all_rules = smir_rules + extra_rules

    if symbolic:
        # Create output directories
        target_llvmdt_path = target_llvm_lib_path / 'dt'

        _LOGGER.info(f'Creating directories {target_llvmdt_path} and {target_hs_path}')
        target_llvmdt_path.mkdir(parents=True, exist_ok=True)
        target_hs_path.mkdir(parents=True, exist_ok=True)

        # Process LLVM definition (only SMIR rules, not extra module rules)
        # Extra module rules are configuration rewrites that LLVM backend doesn't support
        _LOGGER.info('Writing LLVM definition file')
        llvm_lib_dir = kdist.which(llvm_lib_target)
        llvm_def_file = llvm_lib_dir / 'definition.kore'
        llvm_def_output = target_llvm_lib_path / 'definition.kore'
        _insert_rules_and_write(llvm_def_file, smir_rules, llvm_def_output)

        # Run llvm-kompile-matching and llvm-kompile for LLVM
        # TODO use pyk to do this if possible (subprocess wrapper, maybe llvm-kompile itself?)
        # TODO align compilation options to what we use in plugin.py
        import subprocess

        _LOGGER.info('Running llvm-kompile-matching')
        subprocess.run(
            ['llvm-kompile-matching', str(llvm_def_output), 'qbaL', str(target_llvmdt_path), '1/2'], check=True
        )
        _LOGGER.info('Running llvm-kompile')
        subprocess.run(
            [
                'llvm-kompile',
                str(llvm_def_output),
                str(target_llvmdt_path),
                'c',
                '-O2',
                '--',
                '-o',
                target_llvm_lib_path / 'interpreter',
            ],
            check=True,
        )

        # Process Haskell definition (includes both SMIR rules and extra module rules)
        _LOGGER.info('Writing Haskell definition file')
        hs_def_file = haskell_def_dir / 'definition.kore'
        _insert_rules_and_write(hs_def_file, all_rules, target_hs_path / 'definition.kore')

        # Copy all files except definition.kore and binary from HASKELL_DEF_DIR to out/hs
        _LOGGER.info('Copying other artefacts into HS output directory')
        for file_path in haskell_def_dir.iterdir():
            if file_path.name != 'definition.kore' and file_path.name != 'haskellDefinition.bin':
                if file_path.is_file():
                    shutil.copy2(file_path, target_hs_path / file_path.name)
                elif file_path.is_dir():
                    shutil.copytree(file_path, target_hs_path / file_path.name, dirs_exist_ok=True)

        kompile_digest.write(target_dir)
        return KompiledSymbolic(haskell_dir=target_hs_path, llvm_lib_dir=target_llvm_lib_path)

    else:
        target_llvmdt_path = target_llvm_path / 'dt'
        _LOGGER.info(f'Creating directory {target_llvmdt_path}')
        target_llvmdt_path.mkdir(parents=True, exist_ok=True)

        # Process LLVM definition (only SMIR rules for concrete execution)
        _LOGGER.info('Writing LLVM definition file')
        llvm_def_dir = kdist.which(llvm_target)
        llvm_def_file = llvm_def_dir / 'definition.kore'
        llvm_def_output = target_llvm_path / 'definition.kore'
        _insert_rules_and_write(llvm_def_file, smir_rules, llvm_def_output)

        import subprocess

        _LOGGER.info('Running llvm-kompile-matching')
        subprocess.run(
            ['llvm-kompile-matching', str(llvm_def_output), 'qbaL', str(target_llvmdt_path), '1/2'], check=True
        )
        _LOGGER.info('Running llvm-kompile')
        subprocess.run(
            [
                'llvm-kompile',
                str(llvm_def_output),
                str(target_llvmdt_path),
                'main',
                '-O2',
                '--',
                '-o',
                target_llvm_path / 'interpreter',
            ],
            check=True,
        )
        blacklist = ['definition.kore', 'interpreter', 'dt']
        to_copy = [file.name for file in llvm_def_dir.iterdir() if file.name not in blacklist]
        for file in to_copy:
            _LOGGER.info(f'Copying file {file}')
            shutil.copy2(llvm_def_dir / file, target_llvm_path / file)

        kompile_digest.write(target_dir)
        return KompiledConcrete(llvm_dir=target_llvm_path)


def _make_stratified_rules(
    kmir: KMIR,
    fun: str,
    arg_sort: str,
    result_sort: str,
    id_cons: str,
    assocs: list[tuple[int, KInner]],
    not_found: KInner,
    strata: int = 10,
) -> Sequence[Sentence]:
    from pyk.kore.prelude import int_dv
    from pyk.kore.rule import FunctionRule

    int_eqls = "Lbl'UndsEqlsEqls'Int'Unds'"
    int_tmod = "Lbl'UndsPerc'Int'Unds'"

    arg_sort_kore = SortApp('Sort' + arg_sort)
    int_sort_kore = SortApp('SortInt')
    result_sort_kore = SortApp('Sort' + result_sort)
    id_cons_kore = 'Lbl' + id_cons

    declarations = [
        # declare stratified functions
        SymbolDecl(
            symbol=Symbol('Lbl' + fun + str(i)),
            param_sorts=(int_sort_kore,),
            sort=result_sort_kore,
            attrs=(
                App('function'),
                App('total'),
            ),
        )
        for i in range(strata)
    ]
    dispatch = [
        # define dispatch equations to stratified functions
        # f'rule {fun}({id_cons}(N) => {fun}{i}(N)) requires N /Int {strata} ==Int {i}'
        FunctionRule(
            App('Lbl' + fun, (), (App(id_cons_kore, (), (EVar('VarN', int_sort_kore),)),)),
            App('Lbl' + fun + str(i), (), (EVar('VarN', int_sort_kore),)),
            App(int_eqls, (), [App(int_tmod, (), [EVar('VarN', int_sort_kore), int_dv(strata)]), int_dv(i)]),
            None,
            result_sort_kore,
            (arg_sort_kore,),
            None,
            0,
            f'{fun}{i}-dispatch',
            f'{fun}{i}-dispatch',
        )
        .to_axiom()
        .let_attrs((App("UNIQUE'Unds'ID", (), (String(f'{fun}{i}-dispatch'),)),))
        for i in range(strata)
    ]
    defaults = [
        # define dispatch equations to stratified functions
        # f'rule {fun}{i}(N) => {default} [owise]'
        FunctionRule(
            App('Lbl' + fun + str(i), (), (EVar('VarN', SortApp('SortInt')),)),
            kmir.kast_to_kore(not_found, KSort(result_sort)),
            None,
            None,
            result_sort_kore,
            (int_sort_kore,),
            None,
            200,
            f'{fun}{i}-default',
            f'{fun}{i}-default',
        )
        .to_axiom()
        .let_attrs((App('owise'), App("UNIQUE'Unds'ID", (), (String(f'{fun}{i}-default'),))))
        for i in range(strata)
    ]
    equations = []
    for i, result in assocs:
        m = i % strata
        equations.append(
            _mk_equation(kmir, fun + str(m), intToken(i), 'Int', result, result_sort).let_attrs(
                (App("UNIQUE'Unds'ID", (), (String(f'{fun}{m}-{i}-generated'),)),)
            )
        )
    return [*declarations, *dispatch, *defaults, *equations]


def make_kore_rules(kmir: KMIR, smir_info: SMIRInfo) -> Sequence[Sentence]:
    # kprint tool is too chatty
    kprint_logger = logging.getLogger('pyk.ktool.kprint')
    kprint_logger.setLevel(logging.WARNING)

    unknown_function = KApply(
        'MonoItemKind::MonoItemFn',
        (
            KApply('symbol(_)_LIB_Symbol_String', (KToken('"** UNKNOWN FUNCTION **"', KSort('String')),)),
            KApply('defId(_)_BODY_DefId_Int', (KVariable('TY', KSort('Int')),)),
            KApply('noBody_BODY_MaybeBody', ()),
        ),
    )
    default_function = _mk_equation(
        kmir, 'lookupFunction', KApply('ty', (KVariable('TY'),)), 'Ty', unknown_function, 'MonoItemKind'
    ).let_attrs(((App('owise')),))

    equations: list[Axiom] = [default_function]

    for fty, kind in _functions(kmir, smir_info).items():
        equations.append(
            _mk_equation(kmir, 'lookupFunction', KApply('ty', (intToken(fty),)), 'Ty', kind, 'MonoItemKind')
        )

    # stratify type and alloc lookups
    def get_int_arg(app: KInner) -> int:
        match app:
            case KApply(_, args=(KToken(token=int_arg, sort=KSort('Int')),)):
                return int(int_arg)
            case _:
                raise Exception(f'Cannot extract int arg from {app}')

    invalid_type = KApply('TypeInfo::VoidType', ())
    parsed_types = [kmir.parser.parse_mir_json(type, 'TypeMapping') for type in smir_info._smir['types']]
    type_mappings = [type_mapping for type_mapping, _ in (result for result in parsed_types if result is not None)]

    type_assocs = [
        (get_int_arg(ty), info)
        for ty, info in (type_mapping.args for type_mapping in type_mappings if isinstance(type_mapping, KApply))
    ]

    type_equations = _make_stratified_rules(kmir, 'lookupTy', 'Ty', 'TypeInfo', 'ty', type_assocs, invalid_type)

    invalid_alloc_n = KApply(
        'InvalidAlloc(_)_RT-VALUE-SYNTAX_Evaluation_AllocId', (KApply('allocId', (KVariable('N'),)),)
    )
    decoded_allocs = [_decode_alloc(smir_info=smir_info, raw_alloc=alloc) for alloc in smir_info._smir['allocs']]
    allocs = [(get_int_arg(alloc_id), value) for (alloc_id, value) in decoded_allocs]
    alloc_equations = _make_stratified_rules(
        kmir, 'lookupAlloc', 'AllocId', 'Evaluation', 'allocId', allocs, invalid_alloc_n
    )

    return [*equations, *type_equations, *alloc_equations]


def _functions(kmir: KMIR, smir_info: SMIRInfo) -> dict[int, KInner]:
    functions: dict[int, KInner] = {}

    # Parse regular functions
    for item_name, item in smir_info.items.items():
        if not item_name in smir_info.function_symbols_reverse:
            _LOGGER.warning(f'Item not found in SMIR: {item_name}')
            continue
        parsed_item = kmir.parser.parse_mir_json(item, 'MonoItem')
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
                [KApply('symbol(_)_LIB_Symbol_String', [stringToken(sym['IntrinsicSym'])])],
            )

    return functions


def _mk_equation(kmir: KMIR, fun: str, arg: KInner, arg_sort: str, result: KInner, result_sort: str) -> Axiom:
    from pyk.kore.rule import FunctionRule
    from pyk.kore.syntax import App, SortApp

    arg_kore = kmir.kast_to_kore(arg, KSort(arg_sort))
    fun_app = App('Lbl' + fun, (), (arg_kore,))
    result_kore = kmir.kast_to_kore(result, KSort(result_sort))

    assert isinstance(fun_app, App)
    rule = FunctionRule(
        lhs=fun_app,
        rhs=result_kore,
        req=None,
        ens=None,
        sort=SortApp('Sort' + result_sort),
        arg_sorts=(SortApp('Sort' + arg_sort),),
        anti_left=None,
        priority=50,
        uid='fubar',
        label='fubaz',
    )
    return rule.to_axiom()


def _decode_alloc(smir_info: SMIRInfo, raw_alloc: Any) -> tuple[KInner, KInner]:
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


def _insert_rules_and_write(input_file: Path, rules: Sequence[Sentence], output_file: Path) -> None:
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # last line must start with 'endmodule'
    last_line = lines[-1]
    assert last_line.startswith('endmodule')
    new_lines = lines[:-1]

    # Insert rules before the endmodule line
    new_lines.append(f'\n// Generated from file {input_file}\n\n')
    new_lines.extend([ax.text + '\n' for ax in rules])
    new_lines.append('\n' + last_line)

    # Write to output file
    with open(output_file, 'w') as f:
        f.writelines(new_lines)
