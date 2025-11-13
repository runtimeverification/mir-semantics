from __future__ import annotations

import json
import logging
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply, KSort
from pyk.kast.prelude.kint import intToken
from pyk.kast.prelude.string import stringToken

from .build import HASKELL_DEF_DIR, LLVM_DEF_DIR, LLVM_LIB_DIR
from .kmir import KMIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Final

    from pyk.kast import KInner
    from pyk.kore.syntax import Axiom

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

    @staticmethod
    def load(target_dir: Path) -> KompileDigest:
        digest_file = KompileDigest._digest_file(target_dir)

        if not digest_file.exists():
            raise ValueError(f'Digest file does not exist: {digest_file}')

        data = json.loads(digest_file.read_text())
        return KompileDigest(
            digest=data['digest'],
            symbolic=data['symbolic'],
        )

    def write(self, target_dir: Path) -> None:
        self._digest_file(target_dir).write_text(
            json.dumps(
                {
                    'digest': self.digest,
                    'symbolic': self.symbolic,
                },
            ),
        )

    @staticmethod
    def _digest_file(target_dir: Path) -> Path:
        return target_dir / 'smir-digest.json'


def kompile_smir(
    smir_info: SMIRInfo,
    target_dir: Path,
    bug_report: Path | None = None,
    symbolic: bool = True,
) -> KompiledSMIR:
    kompile_digest: KompileDigest | None = None
    try:
        kompile_digest = KompileDigest.load(target_dir)
    except Exception:
        pass

    target_hs_path = target_dir / 'haskell'
    target_llvm_lib_path = target_dir / 'llvm-library'
    target_llvm_path = target_dir / 'llvm'

    if kompile_digest is not None and kompile_digest.digest == smir_info.digest and kompile_digest.symbolic == symbolic:
        _LOGGER.info(f'Kompiled SMIR up-to-date, no kompilation necessary: {target_dir}')
        if symbolic:
            return KompiledSymbolic(haskell_dir=target_hs_path, llvm_lib_dir=target_llvm_lib_path)
        else:
            return KompiledConcrete(llvm_dir=target_llvm_path)

    _LOGGER.info(f'Kompiling SMIR program: {target_dir}')

    kompile_digest = KompileDigest(digest=smir_info.digest, symbolic=symbolic)
    target_dir.mkdir(parents=True, exist_ok=True)

    kmir = KMIR(HASKELL_DEF_DIR)
    rules = make_kore_rules(kmir, smir_info)
    _LOGGER.info(f'Generated {len(rules)} function equations to add to `definition.kore')

    if symbolic:
        # Create output directories
        target_llvmdt_path = target_llvm_lib_path / 'dt'

        _LOGGER.info(f'Creating directories {target_llvmdt_path} and {target_hs_path}')
        target_llvmdt_path.mkdir(parents=True, exist_ok=True)
        target_hs_path.mkdir(parents=True, exist_ok=True)

        # Process LLVM definition
        _LOGGER.info('Writing LLVM definition file')
        llvm_def_file = LLVM_LIB_DIR / 'definition.kore'
        llvm_def_output = target_llvm_lib_path / 'definition.kore'
        _insert_rules_and_write(llvm_def_file, rules, llvm_def_output)

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

        # Process Haskell definition
        _LOGGER.info('Writing Haskell definition file')
        hs_def_file = HASKELL_DEF_DIR / 'definition.kore'
        _insert_rules_and_write(hs_def_file, rules, target_hs_path / 'definition.kore')

        # Copy all files except definition.kore and binary from HASKELL_DEF_DIR to out/hs
        _LOGGER.info('Copying other artefacts into HS output directory')
        for file_path in HASKELL_DEF_DIR.iterdir():
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

        # Process LLVM definition
        _LOGGER.info('Writing LLVM definition file')
        llvm_def_file = LLVM_LIB_DIR / 'definition.kore'
        llvm_def_output = target_llvm_path / 'definition.kore'
        _insert_rules_and_write(llvm_def_file, rules, llvm_def_output)

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
        to_copy = [file.name for file in LLVM_DEF_DIR.iterdir() if file.name not in blacklist]
        for file in to_copy:
            _LOGGER.info(f'Copying file {file}')
            shutil.copy2(LLVM_DEF_DIR / file, target_llvm_path / file)

        kompile_digest.write(target_dir)
        return KompiledConcrete(llvm_dir=target_llvm_path)


def make_kore_rules(kmir: KMIR, smir_info: SMIRInfo) -> list[Axiom]:
    equations = []

    # kprint tool is too chatty
    kprint_logger = logging.getLogger('pyk.ktool.kprint')
    kprint_logger.setLevel(logging.WARNING)

    for fty, kind in _functions(kmir, smir_info).items():
        equations.append(
            _mk_equation(kmir, 'lookupFunction', KApply('ty', (intToken(fty),)), 'Ty', kind, 'MonoItemKind')
        )

    for type in smir_info._smir['types']:
        parse_result = kmir.parser.parse_mir_json(type, 'TypeMapping')
        assert parse_result is not None
        type_mapping, _ = parse_result
        assert isinstance(type_mapping, KApply) and len(type_mapping.args) == 2
        ty, tyinfo = type_mapping.args
        equations.append(_mk_equation(kmir, 'lookupTy', ty, 'Ty', tyinfo, 'TypeInfo'))

    for alloc in smir_info._smir['allocs']:
        alloc_id, value = _decode_alloc(smir_info=smir_info, raw_alloc=alloc)
        equations.append(_mk_equation(kmir, 'lookupAlloc', alloc_id, 'AllocId', value, 'Evaluation'))

    return equations


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


def _insert_rules_and_write(input_file: Path, rules: list[Axiom], output_file: Path) -> None:
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # last line must start with 'endmodule'
    last_line = lines[-1]
    assert last_line.startswith('endmodule')
    new_lines = lines[:-1]

    # Insert rules before the endmodule line
    new_lines.append(f'\n// Generated from file {input_file}\n\n')
    new_lines.extend([ax.text for ax in rules])
    new_lines.append('\n' + last_line)

    # Write to output file
    with open(output_file, 'w') as f:
        f.writelines(new_lines)
