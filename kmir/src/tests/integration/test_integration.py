from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.convert_json.convert import from_dict

if TYPE_CHECKING:
    from kmir.tools import Tools

CONVERT_BODY_DATA = (Path(__file__).parent / 'data' / 'convert-body').resolve(strict=True)
CONVERT_BODY_INPUT_DIRS = [CONVERT_BODY_DATA / 'panic']


@pytest.mark.parametrize(
    'test_dir',
    CONVERT_BODY_INPUT_DIRS,
    ids=[str(test_file.relative_to(CONVERT_BODY_DATA)) for test_file in CONVERT_BODY_INPUT_DIRS],
)
def test_parse_body(test_dir: Path, tools: Tools) -> None:
    serialized_json = test_dir / 'serialized.json'
    reference_mir = test_dir / 'reference.kmir'

    with serialized_json.open('r') as f:
        converted_ast = from_dict(json.load(f))

    rc, parsed_ast = tools.kparse.kparse(reference_mir, sort='Body')

    assert converted_ast == parsed_ast
