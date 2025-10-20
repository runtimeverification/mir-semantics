from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.kompile import _functions
from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output

if TYPE_CHECKING:
    from kmir.kmir import KMIR

# Test data for intrinsic blackbox test
EXEC_DATA_DIR = (Path(__file__).parent / 'data' / 'exec-smir').resolve(strict=True)
INTRINSIC_SMIR_FILE = EXEC_DATA_DIR / 'intrinsic' / 'blackbox.smir.json'


@pytest.mark.parametrize('smir_file', [INTRINSIC_SMIR_FILE], ids=['intrinsic_blackbox'])
def test_functions(smir_file: Path, kmir: KMIR, update_expected_output: bool) -> None:
    """Test _make_function_map using actual SMIR JSON data."""
    # Given
    smir_info = SMIRInfo.from_file(smir_file)
    # When
    result = _functions(kmir, smir_info)
    result_dict = {ty: body.to_dict() for ty, body in result.items()}
    # Then
    result_str = json.dumps(result_dict, indent=2, sort_keys=True)
    expected_file = smir_file.parent / 'blackbox_functions.expected.json'
    assert_or_update_show_output(result_str, expected_file, update=update_expected_output)
