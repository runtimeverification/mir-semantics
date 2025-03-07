from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyk.kast.inner import KApply, KSort, KToken, KVariable
from pyk.kast.outer import KClaim
from pyk.proof import Proof

from kmir.__main__ import GenSpecOpts, ProveRunOpts, _kmir_gen_spec, _kmir_prove_run
from kmir.build import haskell_semantics, llvm_semantics
from kmir.convert_from_definition.v2parser import Parser

if TYPE_CHECKING:
    from pyk.kast.inner import KInner
    from collections.abc import Iterable

    from kmir.convert_from_definition.v2parser import JSON
    from kmir.kmir import KMIR
    from kmir.tools import Tools


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
    SCHEMA_PARSE_DATA / 'testsort2',
]


@pytest.mark.parametrize(
    'test_dir',
    SCHEMA_PARSE_INPUT_DIRS,
    ids=[str(test_file.relative_to(SCHEMA_PARSE_DATA)) for test_file in SCHEMA_PARSE_INPUT_DIRS],
)
def test_schema_parse(test_dir: Path, tools: Tools) -> None:
    input_json = test_dir / 'input.json'
    reference_sort = test_dir / 'reference.sort'
    reference_kmir = test_dir / 'reference.kmir'
    parser = Parser(tools.definition)

    with input_json.open('r') as f:
        json_data = json.load(f)
    with reference_sort.open('r') as f:
        reference_sort_data = f.read().rstrip()
    parser_result = parser.parse_mir_json(json_data, reference_sort_data)
    assert parser_result is not None
    converted_ast, _ = parser_result

    rc, parsed_ast = tools.kparse.kparse(reference_kmir, sort=reference_sort_data)

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
    (2, KApply('local(_)_BODY_Local_Int', (KToken('2', KSort('Int')))), KSort('Local')),
    (
        {'StorageLive': 2},
        KApply('StatementKind::StorageLive', (KApply('local(_)_BODY_Local_Int', (KToken('2', KSort('Int')))))),
        KSort('StatementKind'),
    ),
    ('Not', KApply('Mutability::Not', ()), KSort('Mutability')),
    (2, KApply('span(_)_TYPES_Span_Int', (KToken('2', KSort('Int')))), KSort('Span')),
    (9, KApply('ty(_)_TYPES_Ty_Int', (KToken('9', KSort('Int')))), KSort('Ty')),
    (
        {'mutability': 'Mut', 'span': 420, 'ty': 9},
        KApply(
            'localDecl(_,_,_)_BODY_LocalDecl_Ty_Span_Mutability',
            (
                KApply('ty(_)_TYPES_Ty_Int', (KToken('9', KSort('Int')))),
                KApply('span(_)_TYPES_Span_Int', (KToken('420', KSort('Int')))),
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

SCHEMA_PARSE_KAPPLY_DATA = RIGID_TY_TESTS + LOCAL_DECL_TESTS + FUNCTION_SYMBOL_TESTS + BYTES_TESTS


@pytest.mark.parametrize(
    'test_case',
    SCHEMA_PARSE_KAPPLY_DATA,
    ids=[f'{sort.name}-{i}' for i, (_, _, sort) in enumerate(SCHEMA_PARSE_KAPPLY_DATA)],
)
def test_schema_kapply_parse(
    test_case: tuple[JSON, KInner, KSort],
    tools: Tools,
) -> None:
    parser = Parser(tools.definition)

    json_data, expected_term, expected_sort = test_case

    assert parser.parse_mir_json(json_data, expected_sort.name) == (expected_term, expected_sort)


EXEC_DATA_DIR = (Path(__file__).parent / 'data' / 'exec-smir').resolve(strict=True)
EXEC_DATA = [
    (
        'main-a-b-c',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.smir.json',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.run.state',
        None,
    ),
    (
        'main-a-b-c --depth 19',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.smir.json',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.19.state',
        19,
    ),
    (
        'call-with-args',
        EXEC_DATA_DIR / 'call-with-args' / 'main-a-b-with-int.smir.json',
        EXEC_DATA_DIR / 'call-with-args' / 'main-a-b-with-int.23.state',
        23,
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
        EXEC_DATA_DIR / 'structs-tuples' / 'structs-tuples.84.state',
        84,
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
]


@pytest.mark.parametrize('tools', [llvm_semantics(), haskell_semantics()], ids=['llvm', 'haskell'])
@pytest.mark.parametrize(
    'test_case',
    EXEC_DATA,
    ids=[name for (name, _, _, _) in EXEC_DATA],
)
def test_exec_smir(
    test_case: tuple[str, Path, Path, int],
    tools: Tools,
) -> None:

    (_, input_json, output_kast, depth) = test_case

    parser = Parser(tools.definition)

    with input_json.open('r') as f:
        json_data = json.load(f)
    parsed = parser.parse_mir_json(json_data, 'Pgm')
    assert parsed is not None
    kmir_kast, _ = parsed

    result = tools.run_parsed(kmir_kast, depth=depth)

    with output_kast.open('r') as f:
        expected = f.read().rstrip()

    result_pretty = tools.kprint.kore_to_pretty(result).rstrip()

    if os.getenv('UPDATE_EXEC_SMIR') is None:
        assert result_pretty == expected
    else:
        with output_kast.open('w') as f:
            f.write(result_pretty)


@pytest.mark.parametrize(
    'test_data',
    [(name, smir_json) for (name, smir_json, _, depth) in EXEC_DATA if depth is None],
    ids=[name for (name, _, _, depth) in EXEC_DATA if depth is None],
)
def test_prove(test_data: tuple[str, Path], tmp_path: Path, kmir: KMIR) -> None:
    testname, smir_json = test_data
    spec_file = tmp_path / f'{testname}.k'
    gen_opts = GenSpecOpts(smir_json, spec_file, 'main')

    proof_dir = tmp_path / 'proof'
    prove_opts = ProveRunOpts(spec_file, proof_dir, None, None)

    _kmir_gen_spec(gen_opts)
    _kmir_prove_run(prove_opts)

    claim_labels = kmir.get_claim_index(spec_file).labels()
    for label in claim_labels:
        proof = Proof.read_proof_data(proof_dir, label)
        assert proof.passed


def test_prove_binops(kmir: KMIR):
    # creates a claim index from a template by inserting requires clauses
    # from test parameters and runs proofs for all claims in the index

    from pyk.proof.reachability import APRProof, APRProver

    def number(n: int, bits: int = 8, signed: str = "true") -> KInner:
        KApply(
            'Integer(_,_,_)_RT-DATA-HIGH-SYNTAX_Value_Int_Int_Bool',
            ( KToken(str(n), KSort('Int')), KToken(str(bits), KSort('Int')), KToken(signed, KSort('Bool')))
        )

    def typedLocal(val: KInner, ty: KInner = KVariable('?_TY', KSort('MaybeTy')), mut: KInner = KVariable('?_MUT', KSort('Mutability'))):
        KApply('typedLocal(_,_,_)_RT-DATA-SYNTAX_TypedLocal_Value_MaybeTy_Mutability', (val, ty, mut))

    test_data = [
        (
            'addition',
            number(42),
            number(43),
            typedLocal(number(85))
        )
    ]

    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode='w', delete_on_close=False, prefix='claim-template.k') as claim_file:
        claim_file.write(
            '''
module CLAIM-TEMPLATE
  imports KMIR

  claim [binop]:
        <k> rvalueBinaryOp(
                OP,
                operandCopy(place(local(1), .ProjectionElems)),
                operandCopy(place(local(2), .ProjectionElems))
            ) => ?RESULT
        ...
        </k>
        <locals>
          ListItem(noValue( _TY, mutabilityMut))
          ListItem(typedLocal(ARG1, TY:Ty, _MUT1)) // important for the #compute rule to fire!
          ListItem(typedLocal(ARG2, TY, _MUT2))
        </locals>
endmodule'''
        )
        claim_file.close()
        claim_template = kmir.get_claims(Path(claim_file.name))[0]


    def anded(monoms: Iterable[KInner]) -> KInner:
        from functools import reduce
        reduce(lambda x,y: KApply("_andBool_", (x, y)), monoms)

    for name, arg1, arg2, result in test_data:
        claim = claim_template.let(
            requires = anded((KApply("_==K_", (KVariable("ARG1"), arg1)), KApply("_==K_", (KVariable("ARG2"), arg2)))),
            ensures = KApply("_==K_", (KVariable("?RESULT"), result)),
        )

        print(claim)

        proof = APRProof.from_claim(kmir.definition, claim, {})
        with kmir.kcfg_explore(name) as kcfg_explore:
            APRProver(kcfg_explore).advance_proof(proof)
            assert proof.passed, f"Proof binop-{name} failed."
