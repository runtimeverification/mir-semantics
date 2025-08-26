from __future__ import annotations

import json
from pathlib import Path

import pytest

from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output


def _test_smir_property(smir_file: Path, property_name: str, update_expected_output: bool) -> None:
    """Template function for testing SMIR properties."""
    smir_info = SMIRInfo.from_file(smir_file)

    # Get the property value dynamically
    result = getattr(smir_info, property_name)

    # Convert result to a formatted string for comparison
    result_str = json.dumps(result, indent=2, sort_keys=True)

    # Use assert_or_update_show_output for comparison
    expected_file = smir_file.parent / f'blackbox_{property_name}.expected.json'
    assert_or_update_show_output(result_str, expected_file, update=update_expected_output)


# Test data for intrinsic blackbox test - need to look in integration/data
INTEGRATION_DATA_DIR = Path(__file__).parent.parent / 'integration' / 'data' / 'exec-smir'
INTRINSIC_SMIR_FILE = INTEGRATION_DATA_DIR / 'intrinsic' / 'blackbox.smir.json'


@pytest.mark.parametrize('smir_file', [INTRINSIC_SMIR_FILE], ids=['intrinsic_blackbox'])
def test_function_symbols(smir_file: Path, update_expected_output: bool) -> None:
    """Test function_symbols using actual SMIR JSON data."""
    _test_smir_property(smir_file, 'function_symbols', update_expected_output)


@pytest.mark.parametrize('smir_file', [INTRINSIC_SMIR_FILE], ids=['intrinsic_blackbox'])
def test_function_symbols_reverse(smir_file: Path, update_expected_output: bool) -> None:
    """Test function_symbols_reverse using actual SMIR JSON data."""
    _test_smir_property(smir_file, 'function_symbols_reverse', update_expected_output)


@pytest.mark.parametrize('smir_file', [INTRINSIC_SMIR_FILE], ids=['intrinsic_blackbox'])
def test_function_tys(smir_file: Path, update_expected_output: bool) -> None:
    """Test function_tys using actual SMIR JSON data."""
    _test_smir_property(smir_file, 'function_tys', update_expected_output)
