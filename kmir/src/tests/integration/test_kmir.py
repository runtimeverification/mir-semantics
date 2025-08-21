from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output

from ..utils import filter_test_files, get_expected_path

if TYPE_CHECKING:
    from pathlib import Path

    from kmir.kmir import KMIR

# Common parametrization data - using the same test data as test_smir.py
SIMPLE_TEST_DATA = filter_test_files(r'intrinsic/blackbox')
SMIR_TEST_DATA = [smir_file for _, _, smir_file in SIMPLE_TEST_DATA]
SMIR_TEST_IDS = [name for name, _, _ in SIMPLE_TEST_DATA]


@pytest.mark.parametrize('smir_file', SMIR_TEST_DATA, ids=SMIR_TEST_IDS)
def test_functions(smir_file: Path, kmir: KMIR, update_expected_output: bool, request: pytest.FixtureRequest) -> None:
    """Test _make_function_map using actual SMIR JSON data from tests/smir/."""
    # Given
    smir_info = SMIRInfo.from_file(smir_file)
    # When
    result = kmir.functions(smir_info)
    result_dict = {ty: body.to_dict() for ty, body in result.items()}
    # Then
    result_str = json.dumps(result_dict, indent=2, sort_keys=True)
    expected_file = get_expected_path(request, 'json')
    assert_or_update_show_output(result_str, expected_file, update=update_expected_output)
