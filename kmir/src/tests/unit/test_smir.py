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


def test_call_edges_preserve_drop_glue_for_downcast_field() -> None:
    smir_info = SMIRInfo(
        {
            'name': 'drop-downcast-field',
            'allocs': [],
            'types': [
                [
                    1,
                    {
                        'EnumType': {
                            'name': 'Wrapper',
                            'adt_def': 1,
                            'discriminants': [0],
                            'fields': [[2]],
                            'layout': None,
                        }
                    },
                ],
                [
                    2,
                    {
                        'StructType': {
                            'name': 'Inner',
                            'adt_def': 2,
                            'fields': [],
                            'layout': None,
                        }
                    },
                ],
                [3, {'PtrType': {'pointee_type': 2}}],
            ],
            'functions': [
                [10, {'NormalSym': 'caller'}],
                [12, {'NormalSym': 'drop_inner'}],
            ],
            'items': [
                {
                    'symbol_name': 'caller',
                    'mono_item_kind': {
                        'MonoItemFn': {
                            'name': 'caller',
                            'body': {
                                'arg_count': 0,
                                'locals': [{'ty': 0}, {'ty': 1}],
                                'blocks': [
                                    {
                                        'terminator': {
                                            'kind': {
                                                'Drop': {
                                                    'place': {
                                                        'local': 1,
                                                        'projection': [{'Downcast': 0}, {'Field': [0, 2]}],
                                                    },
                                                    'target': 0,
                                                    'unwind': 'Continue',
                                                }
                                            }
                                        }
                                    }
                                ],
                            },
                        }
                    },
                },
                {
                    'symbol_name': 'drop_inner',
                    'mono_item_kind': {
                        'MonoItemFn': {
                            'name': 'std::ptr::drop_in_place::<Inner>',
                            'body': {
                                'arg_count': 1,
                                'locals': [{'ty': 0}, {'ty': 3}],
                                'blocks': [],
                            },
                        }
                    },
                },
            ],
            'spans': [],
        }
    )

    assert smir_info.call_edges == {10: {12}, 12: set()}
