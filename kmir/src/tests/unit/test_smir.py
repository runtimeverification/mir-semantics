from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output
from ..utils import get_test_files, get_expected_path

if TYPE_CHECKING:
    from kmir.smir import Ty


# Test data for parametrization
TEST_FILES = get_test_files()


@pytest.mark.parametrize("test_name,rust_file,smir_file", TEST_FILES, ids=[name for name, _, _ in TEST_FILES])
def test_function_symbols_reverse(test_name: str, rust_file: Path, smir_file: Path, update_expected_output: bool, request) -> None:
    """Test function_symbols_reverse using actual SMIR JSON data from tests/smir/."""
    print(f"Testing with {rust_file} -> {smir_file}")
    
    # Load the SMIR JSON data
    with open(smir_file, 'r') as f:
        smir_data = json.load(f)
    
    smir_info = SMIRInfo(smir_data)
    result = smir_info.function_symbols_reverse
    
    # Convert result to a formatted string for comparison
    result_str = json.dumps(result, indent=2, sort_keys=True)
    
    # Use assert_or_update_show_output for comparison
    expected_file = get_expected_path(request, 'json')
    assert_or_update_show_output(result_str, expected_file, update=update_expected_output)
    
    print(f"✓ {test_name}: Found {len(result)} function symbols")
