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
    # This SMIR models:
    #   local 1: Wrapper
    #   Drop(local 1 . Downcast(0) . Field(0, Inner))
    # so `call_edges` must keep the reachable `std::ptr::drop_in_place::<Inner>` callee.
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


def test_call_edges_preserve_drop_glue_for_index_projection() -> None:
    # This SMIR models:
    #   local 1: [Inner; 2]
    #   local 2: usize
    #   Drop(local 1 . Index(local 2))
    # so `call_edges` must keep the reachable `std::ptr::drop_in_place::<Inner>` callee.
    smir_info = SMIRInfo(
        {
            'name': 'drop-index-field',
            'allocs': [],
            'types': [
                [1, {'ArrayType': {'elem_type': 2, 'size': None}}],
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
                [3, {'PrimitiveType': {'Uint': 'Usize'}}],
                [4, {'PtrType': {'pointee_type': 2}}],
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
                                'locals': [{'ty': 0}, {'ty': 1}, {'ty': 3}],
                                'blocks': [
                                    {
                                        'terminator': {
                                            'kind': {
                                                'Drop': {
                                                    'place': {
                                                        'local': 1,
                                                        'projection': [{'Index': 2}],
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
                                'locals': [{'ty': 0}, {'ty': 4}],
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


def test_drop_function_tys_accept_core_drop_in_place_names() -> None:
    smir_info = SMIRInfo(
        {
            'name': 'core-drop-glue',
            'allocs': [],
            'types': [
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
                [12, {'NormalSym': 'drop_inner'}],
            ],
            'items': [
                {
                    'symbol_name': 'drop_inner',
                    'mono_item_kind': {
                        'MonoItemFn': {
                            'name': 'core::ptr::drop_in_place::<Inner>',
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

    assert smir_info.drop_function_tys == {2: 12}


PROVE_DATA_DIR = Path(__file__).parent.parent / 'integration' / 'data' / 'prove-rs'
SUBSLICE_SMIR_FILE = PROVE_DATA_DIR / 'subslice-drop-partial-move.smir.json'

DROP_IN_PLACE_DROPPABLE_2 = (
    '_ZN4core3ptr79drop_in_place'
    '$LT$$u5b$subslice_drop_partial_move..Droppable$u3b$$u20$2$u5d$$GT$'
    '17haa85988f30869bfeE'
)


def test_reduce_to_preserves_subslice_drop_glue() -> None:
    # Generated from subslice-drop-partial-move.rs:
    #   let arr = [Droppable(1), Droppable(2), Droppable(3)];
    #   let [first, ..] = arr;
    #   consume(first);
    #
    # The compiler emits Drop(arr.Subslice(1, 3, false)) to drop the
    # remaining [Droppable; 2].  _projected_ty() must resolve the
    # Subslice to [Droppable; 2] so reduce_to('main') keeps
    # drop_in_place::<[Droppable; 2]>.
    smir_info = SMIRInfo.from_file(SUBSLICE_SMIR_FILE)
    reduced = smir_info.reduce_to('main')
    assert DROP_IN_PLACE_DROPPABLE_2 in reduced.items
