from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

import pytest

if TYPE_CHECKING:
    from typing import Final


class _TestData(NamedTuple):
    symbol: str
    name: str
    expected_demangled: str
    expected_qualified: str


TEST_DATA: Final[tuple[_TestData, ...]] = (
    _TestData(
        symbol='_ZN14small_test_lib3add17h67a713ff87afe55cE',
        name='add',
        expected_demangled='small_test_lib::add::h67a713ff87afe55c',
        expected_qualified='small_test_lib::add',
    ),
    _TestData(
        symbol='_ZN14small_test_lib6assume17h9c6e78f80476cd7fE',
        name='assume',
        expected_demangled='small_test_lib::assume::h9c6e78f80476cd7f',
        expected_qualified='small_test_lib::assume',
    ),
    _TestData(
        symbol='_ZN14small_test_lib7testing17test_add_in_range17h810360fe730dd322E',
        name='testing::test_add_in_range',
        expected_demangled='small_test_lib::testing::test_add_in_range::h810360fe730dd322',
        expected_qualified='small_test_lib::testing::test_add_in_range',
    ),
    _TestData(
        symbol='_ZN42_$LT$$RF$T$u20$as$u20$core..fmt..Debug$GT$3fmt17h3e83eb3d49c5b5a8E',
        name='<&u128 as std::fmt::Debug>::fmt',
        expected_demangled='<&T as core::fmt::Debug>::fmt::h3e83eb3d49c5b5a8',
        expected_qualified='<&u128 as std::fmt::Debug>::fmt',
    ),
    _TestData(
        symbol='_ZN4core3fmt3num51_$LT$impl$u20$core..fmt..Debug$u20$for$u20$u128$GT$3fmt17hfb9d82c7f008e36bE',
        name='core::fmt::num::<impl std::fmt::Debug for u128>::fmt',
        expected_demangled='core::fmt::num::<impl core::fmt::Debug for u128>::fmt::hfb9d82c7f008e36b',
        expected_qualified='core::fmt::num::<impl std::fmt::Debug for u128>::fmt',
    ),
    _TestData(
        symbol='_ZN4core3ptr29drop_in_place$LT$$RF$u128$GT$17hb88ca2b7d29bccccE',
        name='std::ptr::drop_in_place::<&u128>',
        expected_demangled='core::ptr::drop_in_place::<&u128>::hb88ca2b7d29bcccc',
        expected_qualified='std::ptr::drop_in_place::<&u128>',
    ),
    _TestData(
        symbol='_ZN4core9panicking13assert_failed17hdf64d315df90cf99E',
        name='core::panicking::assert_failed::<u128, u128>',
        expected_demangled='core::panicking::assert_failed::hdf64d315df90cf99',
        expected_qualified='core::panicking::assert_failed::<u128, u128>',
    ),
    _TestData(
        symbol='_ZN3std2rt10lang_start28_$u7b$$u7b$closure$u7d$$u7d$17h1f955f4ce95634f1E',
        name='std::rt::lang_start::<()>::{closure#0}',
        expected_demangled='std::rt::lang_start::{{closure}}::h1f955f4ce95634f1',
        expected_qualified='std::rt::lang_start::<()>::{closure#0}',
    ),
    _TestData(
        symbol='_ZN4core3ops8function6FnOnce40call_once$u7b$$u7b$vtable.shim$u7d$$u7d$17ha8802a5f1fccb12bE',
        name='<{closure@std::rt::lang_start<()>::{closure#0}} as std::ops::FnOnce<()>>::call_once',
        expected_demangled='core::ops::function::FnOnce::call_once{{vtable.shim}}::ha8802a5f1fccb12b',
        expected_qualified='core::ops::function::<{closure@std::rt::lang_start<()>::{closure#0}} as std::ops::FnOnce<()>>::call_once',
    ),
    _TestData(
        symbol='_ZN4core6option15Option$LT$T$GT$3map17h5b7d515e7f40e720E',
        name='std::option::Option::<isize>::map::<crate1:MMyEnum, {closure@src/main.rs:19:29: 19:32}>',
        expected_demangled='core::option::Option::<T>::map::h5b7d515e7f40e720',
        expected_qualified='std::option::Option::<isize>::map::<crate1:MMyEnum, {closure@src/main.rs:19:29: 19:32}>',
    ),
)


@pytest.mark.parametrize(
    'symbol,_name,expected,_qualified',
    TEST_DATA,
    ids=[symbol for symbol, *_ in TEST_DATA],
)
def test_demangle(
    symbol: str,
    _name: str,
    expected: str,
    _qualified: str,
) -> None:
    from kmir.linker import _demangle

    # When
    actual = _demangle(symbol=symbol)

    # Then
    assert expected == actual


@pytest.mark.parametrize(
    'symbol_name,name,_demangled,expected',
    TEST_DATA,
    ids=[symbol_name for symbol_name, *_ in TEST_DATA],
)
def test_mono_item_fn_name(
    symbol_name: str,
    name: str,
    _demangled: str,
    expected: str,
) -> None:
    from kmir.linker import _mono_item_fn_name

    # When
    actual = _mono_item_fn_name(symbol_name=symbol_name, name=name)

    # Then
    assert expected == actual
