from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyk.cterm.show import CTermShow
from pyk.kast.inner import KApply, KSort, KToken
from pyk.kast.pretty import PrettyPrinter
from pyk.proof.show import APRProofShow

from kmir.cargo import CargoProject
from kmir.kmir import KMIR, KMIRAPRNodePrinter
from kmir.options import ProveRSOpts, ShowOpts
from kmir.parse.parser import Parser
from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output

if TYPE_CHECKING:
    from pyk.kast.inner import KInner

    from kmir.parse.parser import JSON


PROVE_RS_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)
PROVE_RS_FILES = list(PROVE_RS_DIR.glob('*.*'))
PROVE_RS_START_SYMBOLS = {
    'symbolic-args-fail': ['main', 'eats_all_args'],
    'symbolic-structs-fail': ['eats_struct_args'],
    'unchecked_arithmetic': ['unchecked_add_i32', 'unchecked_sub_usize', 'unchecked_mul_isize'],
    'checked_arithmetic-fail': ['checked_add_i32'],
    'pointer-cast': ['main', 'test'],
    'pointer-cast-length-test-fail': ['array_cast_test'],
    'assume-cheatcode': ['check_assume'],
    'assume-cheatcode-conflict-fail': ['check_assume_conflict'],
}
PROVE_RS_SHOW_SPECS = [
    'local-raw-fail',
    'interior-mut-fail',
    'interior-mut2-fail',
    'interior-mut3-fail',
    'assert_eq_exp',
    'bitwise-not-shift',
    'symbolic-args-fail',
    'symbolic-structs-fail',
    'checked_arithmetic-fail',
    'offset-u8-fail',
    'pointer-cast-length-test-fail',
    'closure_access_struct',
    'niche-enum',
    'assume-cheatcode-conflict-fail',
]


@pytest.mark.parametrize(
    'rs_file',
    PROVE_RS_FILES,
    ids=[spec.stem for spec in PROVE_RS_FILES],
)
def test_prove_rs(rs_file: Path, kmir: KMIR, update_expected_output: bool) -> None:
    should_fail = rs_file.stem.endswith('fail')
    should_show = rs_file.stem in PROVE_RS_SHOW_SPECS
    is_smir = rs_file.suffix == '.json'

    if update_expected_output and not should_show:
        pytest.skip()

    prove_rs_opts = ProveRSOpts(rs_file, smir=is_smir)
    printer = PrettyPrinter(kmir.definition)
    cterm_show = CTermShow(printer.print)

    start_symbols = ['main']
    if rs_file.stem in PROVE_RS_START_SYMBOLS:
        start_symbols = PROVE_RS_START_SYMBOLS[rs_file.stem]

    for start_symbol in start_symbols:
        prove_rs_opts.start_symbol = start_symbol
        apr_proof = kmir.prove_rs(prove_rs_opts)

        if should_show:
            display_opts = ShowOpts(
                rs_file.parent, apr_proof.id, full_printer=False, smir_info=None, omit_current_body=False
            )
            shower = APRProofShow(kmir.definition, node_printer=KMIRAPRNodePrinter(cterm_show, apr_proof, display_opts))
            show_res = '\n'.join(shower.show(apr_proof))
            assert_or_update_show_output(
                show_res, PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.expected', update=update_expected_output
            )

        if not should_fail:
            assert apr_proof.passed
        else:
            assert apr_proof.failed


MULTI_CRATE_DIR = (Path(__file__).parent / 'data' / 'crate-tests').resolve(strict=True)
MULTI_CRATE_TESTS = list(MULTI_CRATE_DIR.glob('*/main-crate'))


@pytest.mark.parametrize(
    'main_crate',
    MULTI_CRATE_TESTS,
    ids=[spec.parent.stem for spec in MULTI_CRATE_TESTS],
)
def test_crate_examples(main_crate: Path, kmir: KMIR, update_expected_output: bool) -> None:
    cargo = CargoProject(main_crate)

    linked = cargo.smir_for_project(clean=True)

    # results for `run` have unstable IDs so run a termination proof for testing
    _, linked_file_str = tempfile.mkstemp()
    linked_file = Path(linked_file_str)
    linked.dump(linked_file)

    # run proofs for all '<start-symbol>.expected' files (failing or not)
    for file in main_crate.parent.glob('*.expected'):
        opts = ProveRSOpts(linked_file, smir=True, start_symbol=file.stem)
        proof = kmir.prove_rs(opts)

        printer = PrettyPrinter(kmir.definition)
        cterm_show = CTermShow(printer.print)
        display_opts = ShowOpts(
            linked_file.parent, proof.id, full_printer=False, smir_info=None, omit_current_body=False
        )
        shower = APRProofShow(kmir.definition, node_printer=KMIRAPRNodePrinter(cterm_show, proof, display_opts))
        spans_removed = [line for line in shower.show(proof) if 'span: ' not in line]
        show_res = '\n'.join(spans_removed)

        assert_or_update_show_output(show_res, file, update=update_expected_output)
    os.unlink(linked_file)


EXEC_DATA_DIR = (Path(__file__).parent / 'data' / 'exec-smir').resolve(strict=True)
EXEC_DATA = [
    (
        'main-a-b-c',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.smir.json',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.run.state',
        None,
    ),
    (
        'main-a-b-c --depth 20',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.smir.json',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.state',
        20,
    ),
    (
        'call-with-args',
        EXEC_DATA_DIR / 'call-with-args' / 'main-a-b-with-int.smir.json',
        EXEC_DATA_DIR / 'call-with-args' / 'main-a-b-with-int.state',
        30,
    ),
    (
        'assign-cast',
        EXEC_DATA_DIR / 'assign-cast' / 'assign-cast.smir.json',
        EXEC_DATA_DIR / 'assign-cast' / 'assign-cast.state',
        None,
    ),
    (
        'structs-tuples',
        EXEC_DATA_DIR / 'structs-tuples' / 'structs-tuples.smir.json',
        EXEC_DATA_DIR / 'structs-tuples' / 'structs-tuples.state',
        99,
    ),
    (
        'struct-field-update',
        EXEC_DATA_DIR / 'structs-tuples' / 'struct_field_update.smir.json',
        EXEC_DATA_DIR / 'structs-tuples' / 'struct_field_update.state',
        None,
    ),
    (
        'arithmetic',
        EXEC_DATA_DIR / 'arithmetic' / 'arithmetic.smir.json',
        EXEC_DATA_DIR / 'arithmetic' / 'arithmetic.state',
        None,
    ),
    (
        'arithmetic-unchecked',
        EXEC_DATA_DIR / 'arithmetic' / 'arithmetic-unchecked-runs.smir.json',
        EXEC_DATA_DIR / 'arithmetic' / 'arithmetic-unchecked-runs.state',
        None,
    ),
    (
        'unary',
        EXEC_DATA_DIR / 'arithmetic' / 'unary.smir.json',
        EXEC_DATA_DIR / 'arithmetic' / 'unary.state',
        None,
    ),
    (
        'Ref-simple',
        EXEC_DATA_DIR / 'references' / 'simple.smir.json',
        EXEC_DATA_DIR / 'references' / 'simple.state',
        None,
    ),
    (
        'Ref-refAsArg',
        EXEC_DATA_DIR / 'references' / 'refAsArg.smir.json',
        EXEC_DATA_DIR / 'references' / 'refAsArg.state',
        None,
    ),
    (
        'Ref-refAsArg2',
        EXEC_DATA_DIR / 'references' / 'refAsArg2.smir.json',
        EXEC_DATA_DIR / 'references' / 'refAsArg2.state',
        1000,
    ),
    (
        'Ref-refReturned',
        EXEC_DATA_DIR / 'references' / 'refReturned.smir.json',
        EXEC_DATA_DIR / 'references' / 'refReturned.state',
        1000,
    ),
    (
        'Ref-doubleRef',
        EXEC_DATA_DIR / 'references' / 'doubleRef.smir.json',
        EXEC_DATA_DIR / 'references' / 'doubleRef.state',
        None,
    ),
    (
        'Ref-mutableRef',
        EXEC_DATA_DIR / 'references' / 'mutableRef.smir.json',
        EXEC_DATA_DIR / 'references' / 'mutableRef.state',
        1000,
    ),
    (
        'Ref-weirdRefs',
        EXEC_DATA_DIR / 'references' / 'weirdRefs.smir.json',
        EXEC_DATA_DIR / 'references' / 'weirdRefs.state',
        None,
    ),
    ('enum-discriminants', EXEC_DATA_DIR / 'enum' / 'enum.smir.json', EXEC_DATA_DIR / 'enum' / 'enum.state', 135),
    (
        'Array-indexing',
        EXEC_DATA_DIR / 'arrays' / 'array_indexing.smir.json',
        EXEC_DATA_DIR / 'arrays' / 'array_indexing.state',
        None,
    ),
    (
        'Array-index-writes',
        EXEC_DATA_DIR / 'arrays' / 'array_write.smir.json',
        EXEC_DATA_DIR / 'arrays' / 'array_write.state',
        None,
    ),
    (
        'Array-inlined',
        EXEC_DATA_DIR / 'arrays' / 'array_inlined.smir.json',
        EXEC_DATA_DIR / 'arrays' / 'array_inlined.state',
        None,
    ),
    (
        'pointer-cast-length-test',
        EXEC_DATA_DIR / 'pointers' / 'pointer-cast-length-test-fail.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'pointer-cast-length-test-fail.state',
        1000,
    ),
    (
        'ref-ptr-cases',
        EXEC_DATA_DIR / 'pointers' / 'ref_ptr_cases.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'ref_ptr_cases.state',
        1000,
    ),
    (
        'Ref-array-elem-ref',
        EXEC_DATA_DIR / 'references' / 'array_elem_ref.smir.json',
        EXEC_DATA_DIR / 'references' / 'array_elem_ref.state',
        None,
    ),
    (
        'intrinsic-blackbox',
        EXEC_DATA_DIR / 'intrinsic' / 'blackbox.smir.json',
        EXEC_DATA_DIR / 'intrinsic' / 'blackbox.state',
        1000,
    ),
    (
        'raw_eq_simple',
        EXEC_DATA_DIR / 'intrinsic' / 'raw_eq_simple.smir.json',
        EXEC_DATA_DIR / 'intrinsic' / 'raw_eq_simple.state',
        100,
    ),
    (
        'Alloc-array-const-compare',
        EXEC_DATA_DIR / 'allocs' / 'array_const_compare.smir.json',
        EXEC_DATA_DIR / 'allocs' / 'array_const_compare.state',
        None,
    ),
    (
        'Alloc-enum-two-refs-fail',
        EXEC_DATA_DIR / 'allocs' / 'enum-two-refs-fail.smir.json',
        EXEC_DATA_DIR / 'allocs' / 'enum-two-refs-fail.state',
        1000,
    ),
    (
        'Alloc-array-nest-compare',
        EXEC_DATA_DIR / 'allocs' / 'array_nest_compare.smir.json',
        EXEC_DATA_DIR / 'allocs' / 'array_nest_compare.state',
        1000,
    ),
    (
        'niche-enum',
        EXEC_DATA_DIR / 'niche-enum' / 'niche-enum.smir.json',
        EXEC_DATA_DIR / 'niche-enum' / 'niche-enum.state',
        None,
    ),
    (
        'newtype-pubkey',
        EXEC_DATA_DIR / 'newtype-pubkey' / 'newtype-pubkey.smir.json',
        EXEC_DATA_DIR / 'newtype-pubkey' / 'newtype-pubkey.state',
        1000,
    ),
    (
        'struct-multi',
        EXEC_DATA_DIR / 'struct-multi' / 'struct-multi.smir.json',
        EXEC_DATA_DIR / 'struct-multi' / 'struct-multi.state',
        2000,
    ),
    (
        'Ptr-offset_get_unchecked',
        EXEC_DATA_DIR / 'pointers' / 'offset_get_unchecked.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'offset_get_unchecked.state',
        None,
    ),
    (
        'Ptr-offset_read',
        EXEC_DATA_DIR / 'pointers' / 'offset_read.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'offset_read.state',
        2000,
    ),
    (
        'Ptr-offset_write',
        EXEC_DATA_DIR / 'pointers' / 'offset_write.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'offset_write.state',
        2000,
    ),
    (
        'Ptr-offset_struct_field_read',
        EXEC_DATA_DIR / 'pointers' / 'offset_struct_field_read.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'offset_struct_field_read.state',
        2000,
    ),
    (
        'Ptr-offset_struct_field_write',
        EXEC_DATA_DIR / 'pointers' / 'offset_struct_field_write.smir.json',
        EXEC_DATA_DIR / 'pointers' / 'offset_struct_field_write.state',
        2000,
    ),
]





      

@pytest.mark.parametrize('symbolic', [False, True], ids=['llvm', 'haskell'])
@pytest.mark.parametrize(
    'test_case',
    EXEC_DATA,
    ids=[name for (name, _, _, _) in EXEC_DATA],
)
def test_exec_smir(
    test_case: tuple[str, Path, Path, int],
    symbolic: bool,
    update_expected_output: bool,
    tmp_path: Path,
) -> None:
    _, input_json, output_kast, depth = test_case
    smir_info = SMIRInfo.from_file(input_json)
    kmir_backend = KMIR.from_kompiled_kore(smir_info, target_dir=tmp_path, symbolic=symbolic)
    result = kmir_backend.run_smir(smir_info, depth=depth)
    result_pretty = kmir_backend.kore_to_pretty(result).rstrip()
    assert_or_update_show_output(result_pretty, output_kast, update=update_expected_output)


@pytest.mark.parametrize(
    'test_data',
    [(name, smir_json) for (name, smir_json, _, depth) in EXEC_DATA if depth is None],
    ids=[name for (name, _, _, depth) in EXEC_DATA if depth is None],
)
def test_prove_termination(test_data: tuple[str, Path], tmp_path: Path, kmir: KMIR) -> None:
    testname, smir_json = test_data

    prove_rs_opts = ProveRSOpts(rs_file=smir_json, smir=True)

    proof = KMIR.prove_rs(prove_rs_opts)
    assert proof.passed


SCHEMA_PARSE_DATA = (Path(__file__).parent / 'data' / 'schema-parse').resolve(strict=True)
SCHEMA_PARSE_INPUT_DIRS = [
    SCHEMA_PARSE_DATA / 'local',
    SCHEMA_PARSE_DATA / 'maybelocal',
    SCHEMA_PARSE_DATA / 'span',
    SCHEMA_PARSE_DATA / 'statement',
    SCHEMA_PARSE_DATA / 'basicblockidx',
    SCHEMA_PARSE_DATA / 'maybebasicblockidx',
    SCHEMA_PARSE_DATA / 'terminatorkindreturn',
    SCHEMA_PARSE_DATA / 'terminatorkindgoto',
    SCHEMA_PARSE_DATA / 'terminatorreturn',
    SCHEMA_PARSE_DATA / 'terminatorgoto',
    SCHEMA_PARSE_DATA / 'statements',
    SCHEMA_PARSE_DATA / 'basicblock1',
    SCHEMA_PARSE_DATA / 'basicblock2',
    SCHEMA_PARSE_DATA / 'place',
    SCHEMA_PARSE_DATA / 'operand',
    SCHEMA_PARSE_DATA / 'rvaluecast',
    SCHEMA_PARSE_DATA / 'rvalueaggregate',
    SCHEMA_PARSE_DATA / 'statementassign1',
    SCHEMA_PARSE_DATA / 'statementassign2',
    SCHEMA_PARSE_DATA / 'aggregatekindadt',
    SCHEMA_PARSE_DATA / 'functions',
    SCHEMA_PARSE_DATA / 'body',
    SCHEMA_PARSE_DATA / 'monoitem',
    SCHEMA_PARSE_DATA / 'testsort2',
    SCHEMA_PARSE_DATA / 'typeinfoenumtype',
]


@pytest.mark.parametrize(
    'test_dir',
    SCHEMA_PARSE_INPUT_DIRS,
    ids=[str(test_file.relative_to(SCHEMA_PARSE_DATA)) for test_file in SCHEMA_PARSE_INPUT_DIRS],
)
def test_schema_parse(test_dir: Path, kmir: KMIR) -> None:
    input_json = test_dir / 'input.json'
    reference_sort = test_dir / 'reference.sort'
    reference_kmir = test_dir / 'reference.kmir'
    parser = Parser(kmir.definition)

    with input_json.open('r') as f:
        json_data = json.load(f)
    with reference_sort.open('r') as f:
        reference_sort_data = f.read().rstrip()
    parser_result = parser.parse_mir_json(json_data, reference_sort_data)
    assert parser_result is not None
    converted_ast, _ = parser_result

    rc, parsed_ast = kmir.kparse(reference_kmir, sort=reference_sort_data)

    assert converted_ast == parsed_ast


RIGID_TY_TESTS = [
    ({'Int': 'Isize'}, KApply('RigidTy::Int', (KApply('IntTy::Isize'))), KSort('RigidTy')),
    ({'Int': 'I8'}, KApply('RigidTy::Int', (KApply('IntTy::I8'))), KSort('RigidTy')),
    ({'Int': 'I16'}, KApply('RigidTy::Int', (KApply('IntTy::I16'))), KSort('RigidTy')),
    ({'Int': 'I32'}, KApply('RigidTy::Int', (KApply('IntTy::I32'))), KSort('RigidTy')),
    ({'Int': 'I64'}, KApply('RigidTy::Int', (KApply('IntTy::I64'))), KSort('RigidTy')),
    ({'Int': 'I128'}, KApply('RigidTy::Int', (KApply('IntTy::I128'))), KSort('RigidTy')),
    ({'Uint': 'Usize'}, KApply('RigidTy::Uint', (KApply('UintTy::Usize'))), KSort('RigidTy')),
    ({'Uint': 'U8'}, KApply('RigidTy::Uint', (KApply('UintTy::U8'))), KSort('RigidTy')),
    ({'Uint': 'U16'}, KApply('RigidTy::Uint', (KApply('UintTy::U16'))), KSort('RigidTy')),
    ({'Uint': 'U32'}, KApply('RigidTy::Uint', (KApply('UintTy::U32'))), KSort('RigidTy')),
    ({'Uint': 'U64'}, KApply('RigidTy::Uint', (KApply('UintTy::U64'))), KSort('RigidTy')),
    ({'Uint': 'U128'}, KApply('RigidTy::Uint', (KApply('UintTy::U128'))), KSort('RigidTy')),
    ({'Float': 'F16'}, KApply('RigidTy::Float', KApply('FloatTy::F16')), KSort('RigidTy')),
    ({'Float': 'F32'}, KApply('RigidTy::Float', KApply('FloatTy::F32')), KSort('RigidTy')),
    ({'Float': 'F64'}, KApply('RigidTy::Float', KApply('FloatTy::F64')), KSort('RigidTy')),
    ({'Float': 'F128'}, KApply('RigidTy::Float', KApply('FloatTy::F128')), KSort('RigidTy')),
    ({'RigidTy': 'Bool'}, KApply('TyKind::RigidTy', (KApply('RigidTy::Bool'))), KSort('TyKind')),
    (
        {'RigidTy': {'Int': 'I8'}},
        KApply('TyKind::RigidTy', (KApply('RigidTy::Int', (KApply('IntTy::I8'))))),
        KSort('TyKind'),
    ),
    (
        {'RigidTy': {'Uint': 'Usize'}},
        KApply('TyKind::RigidTy', (KApply('RigidTy::Uint', (KApply('UintTy::Usize'))))),
        KSort('TyKind'),
    ),
    (
        {'RigidTy': {'Float': 'F128'}},
        KApply('TyKind::RigidTy', (KApply('RigidTy::Float', (KApply('FloatTy::F128'))))),
        KSort('TyKind'),
    ),
]

LOCAL_DECL_TESTS = [
    (2, KApply('local', (KToken('2', KSort('Int')))), KSort('Local')),
    (
        {'StorageLive': 2},
        KApply('StatementKind::StorageLive', (KApply('local', (KToken('2', KSort('Int')))))),
        KSort('StatementKind'),
    ),
    ('Not', KApply('Mutability::Not', ()), KSort('Mutability')),
    (2, KApply('span', (KToken('2', KSort('Int')))), KSort('Span')),
    (9, KApply('ty', (KToken('9', KSort('Int')))), KSort('Ty')),
    (
        {'mutability': 'Mut', 'span': 420, 'ty': 9},
        KApply(
            'localDecl(_,_,_)_BODY_LocalDecl_Ty_Span_Mutability',
            (
                KApply('ty', (KToken('9', KSort('Int')))),
                KApply('span', (KToken('420', KSort('Int')))),
                KApply('Mutability::Mut', ()),
            ),
        ),
        KSort('LocalDecl'),
    ),
]

FUNCTION_SYMBOL_TESTS = [
    (
        {'NormalSym': 'very normal'},
        KApply(
            'FunctionKind::NormalSym',
            (KApply('symbol(_)_LIB_Symbol_String', (KToken('"very normal"', KSort('String'))))),
        ),
        KSort('FunctionKind'),
    ),
    (
        {'IntrinsicSym': 'intrinsic'},
        KApply(
            'FunctionKind::IntrinsicSym',
            (KApply('symbol(_)_LIB_Symbol_String', (KToken('"intrinsic"', KSort('String'))))),
        ),
        KSort('FunctionKind'),
    ),
    (
        {'NoOpSym': ''},
        KApply('FunctionKind::NoOpSym', (KApply('symbol(_)_LIB_Symbol_String', (KToken('""', KSort('String')))))),
        KSort('FunctionKind'),
    ),
]
BYTES_TESTS = [
    (
        {
            'bytes': [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 33],
            'provenance': {'ptrs': []},
            'align': 42,
            'mutability': 'Not',
        },
        KApply(
            'allocation',
            (
                KToken('b"Hello World!"', KSort('Bytes')),
                KApply('provenanceMap', (KApply('ProvenanceMapEntries::empty', ()))),
                KApply('align', (KToken('42', KSort('Int')))),
                KApply('Mutability::Not', ()),
            ),
        ),
        KSort('Allocation'),
    ),
    (
        {'bytes': [0, 0, 0, 42, None, None, None, None], 'provenance': {'ptrs': []}, 'align': 42, 'mutability': 'Not'},
        KApply(
            'allocation',
            (
                KToken('b"\\x00\\x00\\x00\\x2a\\x00\\x00\\x00\\x00"', KSort('Bytes')),
                KApply('provenanceMap', (KApply('ProvenanceMapEntries::empty', ()))),
                KApply('align', (KToken('42', KSort('Int')))),
                KApply('Mutability::Not', ()),
            ),
        ),
        KSort('Allocation'),
    ),
]

TOKEN_TESTS = [
    (
        {'FunType': 'extern \"rust-call\" fn(()) -> i32'},  # double quotes within string
        KApply('TypeInfo::FunType', (KToken('"extern \\"rust-call\\" fn(()) -> i32"', KSort('String')))),
        KSort('TypeInfo'),
    ),
    # MIRInt and MIRBool literals in context
    (
        {'ConstantIndex': {'offset': 1, 'min_length': 1, 'from_end': True}},
        KApply(
            'ProjectionElem::ConstantIndex',
            (
                KToken('1', KSort('Int')),
                KToken('1', KSort('Int')),
                KToken('true', KSort('Bool')),
            ),
        ),
        KSort('ProjectionElem'),
    ),
    (
        {'kind': {'StorageLive': 42}, 'span': 1},
        KApply(
            'statement(_,_)_BODY_Statement_StatementKind_Span',
            (
                KApply('StatementKind::StorageLive', (KApply('local', (KToken('42', KSort('Int')))))),
                KApply('span', (KToken('1', KSort('Int')))),
            ),
        ),
        KSort('Statement'),
    ),
]

SCHEMA_PARSE_KAPPLY_DATA = RIGID_TY_TESTS + LOCAL_DECL_TESTS + FUNCTION_SYMBOL_TESTS + BYTES_TESTS + TOKEN_TESTS


@pytest.mark.parametrize(
    'test_case',
    SCHEMA_PARSE_KAPPLY_DATA,
    ids=[f'{sort.name}-{i}' for i, (_, _, sort) in enumerate(SCHEMA_PARSE_KAPPLY_DATA)],
)
def test_schema_kapply_parse(
    test_case: tuple[JSON, KInner, KSort],
    kmir: KMIR,
) -> None:
    parser = Parser(kmir.definition)

    json_data, expected_term, expected_sort = test_case

    assert parser.parse_mir_json(json_data, expected_sort.name) == (expected_term, expected_sort)
