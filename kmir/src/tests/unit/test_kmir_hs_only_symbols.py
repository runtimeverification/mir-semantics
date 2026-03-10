from __future__ import annotations

import os

from kmir.kmir import KMIR


def test_hs_only_symbols_from_env_parses_and_deduplicates(monkeypatch) -> None:
    monkeypatch.setenv('KMIR_HS_ONLY_SYMBOLS', ' lookupTy , #getBlocks,lookupTy ,, ')
    assert KMIR.hs_only_symbols_from_env() == ['lookupTy', '#getBlocks']


def test_kore_rpc_booster_command_from_env(monkeypatch) -> None:
    monkeypatch.setenv('KMIR_HS_ONLY_SYMBOLS', 'lookupFunction,#metadataSize')
    assert KMIR.kore_rpc_booster_command_from_env() == [
        'kore-rpc-booster',
        '--hs-only-symbol',
        'lookupFunction',
        '--hs-only-symbol',
        '#metadataSize',
    ]


def test_kore_rpc_booster_command_from_env_empty(monkeypatch) -> None:
    monkeypatch.setitem(os.environ, 'KMIR_HS_ONLY_SYMBOLS', '')
    assert KMIR.kore_rpc_booster_command_from_env() is None
