from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyk.kast.inner import KApply, KSort, KToken, Subst

from kmir.convert_from_definition.v2parser import Parser

if TYPE_CHECKING:
    from pyk.kast.inner import KInner

    from kmir.convert_from_definition.v2parser import JSON
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


SCHEMA_PARSE_KAPPLY_DATA = [
    #    ({'Int': 'Isize'}, KApply('IntTy::Isize'), KSort('IntTy')),
    #    ({'Int': 'I8'}, KApply('IntTy::I8'), KSort('IntTy')),
    #    ({'Int': 'I16'}, KApply('IntTy::I16'), KSort('IntTy')),
    #    ({'Int': 'I32'}, KApply('IntTy::I32'), KSort('IntTy')),
    #    ({'Int': 'I64'}, KApply('IntTy::I64'), KSort('IntTy')),
    #    ({'Int': 'I128'}, KApply('IntTy::I128'), KSort('IntTy')),
    #    ({'Uint': 'Usize'}, KApply('UintTy::Usize'), KSort('UintTy')),
    #    ({'Uint': 'U8'}, KApply('UintTy::U8'), KSort('UintTy')),
    #    ({'Uint': 'U16'}, KApply('UintTy::U16'), KSort('UintTy')),
    #    ({'Uint': 'U32'}, KApply('UintTy::U32'), KSort('UintTy')),
    #    ({'Uint': 'U64'}, KApply('UintTy::U64'), KSort('UintTy')),
    #    ({'Uint': 'U128'}, KApply('UintTy::U128'), KSort('UintTy')),
    #    ({'Float': 'F16'}, KApply('FloatTy::F16'), KSort('FloatTy')),
    #    ({'Float': 'F32'}, KApply('FloatTy::F32'), KSort('FloatTy')),
    #    ({'Float': 'F64'}, KApply('FloatTy::F64'), KSort('FloatTy')),
    #    ({'Float': 'F128'}, KApply('FloatTy::F128'), KSort('FloatTy')),
    #    ({'RigidTy': 'Bool'}, KApply('RigidTy::Bool'), KSort('RigidTy')),
    #    ({'RigidTy': {'Int': 'I8'}}, KApply('RigidTy::Int', (KApply('IntTy::I8'))), KSort('RigidTy')),
    #    ({'RigidTy': {'Uint': 'Usize'}}, KApply('RigidTy::Uint', (KApply('UintTy::Usize'))), KSort('RigidTy')),
    #    ({'RigidTy': {'Float': 'F128'}}, KApply('RigidTy::Float', (KApply('FloatTy::F128'))), KSort('RigidTy')),
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
        'main-a-b-c --depth 15',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.smir.json',
        EXEC_DATA_DIR / 'main-a-b-c' / 'main-a-b-c.15.state',
        15,
    ),
]


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

    subst = Subst({'$PGM': kmir_kast})
    init_config = subst.apply(tools.definition.init_config(KSort('GeneratedTopCell')))
    init_kore = tools.krun.kast_to_kore(init_config, KSort('GeneratedTopCell'))
    result = tools.krun.run_pattern(init_kore, depth=depth)

    with output_kast.open('r') as f:
        expected = f.read().rstrip()

    print(result)

    result_pretty = tools.kprint.kore_to_pretty(result).rstrip()

    assert result_pretty == expected
