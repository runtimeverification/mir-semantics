from __future__ import annotations

import pytest

from kmir.testing.fixtures import _normalize_symbol_hashes


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            '_ZN4core3fmt3num53_$LT$impl$u20$core..fmt..LowerHex$u20$for$u20$u32$GT$3fmt17hb987357f13dc6cc8E',
            '_ZN4core3fmt3num53_$LT$impl$u20$core..fmt..LowerHex$u20$for$u20$u32$GT$3fmt17h<hash>E',
        ),
        (
            '_ZN4core3fmt3num53_$LT$impl$u20$core..fmt..LowerHex$u20$for$u20$u32$GT$3fmt17hb987357f13dc6cc8',
            '_ZN4core3fmt3num53_$LT$impl$u20$core..fmt..LowerHex$u20$for$u20$u32$GT$3fmt17h<hash>',
        ),
        (
            'core::panicking::panic::h941160ead03e2d54',
            'core::panicking::panic::h<hash>',
        ),
    ],
    ids=['generic-mangled-full', 'generic-mangled-truncated', 'demangled'],
)
def test_normalize_symbol_hashes(raw: str, expected: str) -> None:
    assert _normalize_symbol_hashes(raw) == expected
