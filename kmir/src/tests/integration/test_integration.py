from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyk.cterm import CTerm
from pyk.kast.inner import KApply, KLabel, KSequence, KSort

from kmir.convert_json.convert import from_dict
from kmir.convert_from_definition.parser import Parser

if TYPE_CHECKING:
    from pyk.kast.inner import KInner

    from kmir.tools import Tools

CONVERT_BODY_DATA = (Path(__file__).parent / 'data' / 'convert-body').resolve(strict=True)
CONVERT_BODY_INPUT_DIRS = [CONVERT_BODY_DATA / 'panic']


@pytest.mark.parametrize(
    'test_dir',
    CONVERT_BODY_INPUT_DIRS,
    ids=[str(test_file.relative_to(CONVERT_BODY_DATA)) for test_file in CONVERT_BODY_INPUT_DIRS],
)
def test_convert_body(test_dir: Path, tools: Tools) -> None:
    serialized_json = test_dir / 'serialized.json'
    reference_mir = test_dir / 'reference.kmir'

    with serialized_json.open('r') as f:
        converted_ast = from_dict(json.load(f))

    rc, parsed_ast = tools.kparse.kparse(reference_mir, sort='Pgm')

    assert converted_ast == parsed_ast


SCHEMA_PARSE_DATA = [
    ('Isize', {'Int': 'Isize'}, KApply('IntTy::Isize'), KSort('IntTy')),
]


@pytest.mark.parametrize(
    'test_case',
    SCHEMA_PARSE_DATA,
    ids=[str(case[0]) for case in SCHEMA_PARSE_DATA],
)
def test_schema_parse(test_case: tuple[str, dict[object, object], KInner], tools: Tools) -> None:
    parser = Parser(tools.definition)

    _, json_data, expected_term, expected_sort = test_case

    assert parser.parse_mir_json(json_data) == (expected_term, expected_sort)


RUN_PANIC_DATA = (Path(__file__).parent / 'data' / 'run-panic').resolve(strict=True)
RUN_PANIC_INPUT = [RUN_PANIC_DATA / 'simple.kmir']


@pytest.mark.parametrize(
    'test_file',
    RUN_PANIC_INPUT,
    ids=[str(test_file.relative_to(RUN_PANIC_DATA)) for test_file in RUN_PANIC_INPUT],
)
def test_run_panic(test_file: Path, tools: Tools) -> None:
    def _is_panic(config: KInner) -> bool:
        k_cell = CTerm(config).cell('K_CELL')

        match k_cell:
            case KSequence((KApply(KLabel(name='panicked')), *_)):
                return True

        return False

    rc, result = tools.krun.krun(test_file)

    assert rc == 0
    assert _is_panic(result)
