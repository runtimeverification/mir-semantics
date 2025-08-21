from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output

from ..utils import filter_test_files, get_expected_path

if TYPE_CHECKING:
    from pathlib import Path


def _test_smir_property(
    smir_file: Path, property_name: str, update_expected_output: bool, request: pytest.FixtureRequest
) -> None:
    """Template function for testing SMIR properties."""
    smir_info = SMIRInfo.from_file(smir_file)

    # Get the property value dynamically
    result = getattr(smir_info, property_name)

    # Convert result to a formatted string for comparison
    result_str = json.dumps(result, indent=2, sort_keys=True)

    # Use assert_or_update_show_output for comparison
    expected_file = get_expected_path(request, 'json')
    assert_or_update_show_output(result_str, expected_file, update=update_expected_output)


# Common parametrization data
SIMPLE_TEST_DATA = filter_test_files(r'intrinsic/blackbox')
SMIR_TEST_DATA = [smir_file for _, _, smir_file in SIMPLE_TEST_DATA]
SMIR_TEST_IDS = [name for name, _, _ in SIMPLE_TEST_DATA]


@pytest.mark.parametrize('smir_file', SMIR_TEST_DATA, ids=SMIR_TEST_IDS)
def test_function_symbols(smir_file: Path, update_expected_output: bool, request: pytest.FixtureRequest) -> None:
    """Test function_symbols using actual SMIR JSON data from tests/smir/."""
    _test_smir_property(smir_file, 'function_symbols', update_expected_output, request)


@pytest.mark.parametrize('smir_file', SMIR_TEST_DATA, ids=SMIR_TEST_IDS)
def test_function_symbols_reverse(
    smir_file: Path, update_expected_output: bool, request: pytest.FixtureRequest
) -> None:
    """Test function_symbols_reverse using actual SMIR JSON data from tests/smir/."""
    _test_smir_property(smir_file, 'function_symbols_reverse', update_expected_output, request)


@pytest.mark.parametrize('smir_file', SMIR_TEST_DATA, ids=SMIR_TEST_IDS)
def test_function_tys(smir_file: Path, update_expected_output: bool, request: pytest.FixtureRequest) -> None:
    """Test function_symbols_reverse using actual SMIR JSON data from tests/smir/."""
    _test_smir_property(smir_file, 'function_tys', update_expected_output, request)
