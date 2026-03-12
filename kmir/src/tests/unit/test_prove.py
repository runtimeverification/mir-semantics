from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from kmir import _prove

if TYPE_CHECKING:
    from pyk.proof.reachability import APRProof

    from kmir.kmir import KMIR
    from kmir.options import ProveRSOpts


def test_prove_parallel_uses_kore_server_without_llvm_library(monkeypatch) -> None:
    opts = cast(
        'ProveRSOpts',
        SimpleNamespace(
            max_workers=2,
            terminate_on_thunk=False,
            max_depth=None,
            max_iterations=None,
            fail_fast=False,
            maintenance_rate=1,
        ),
    )
    kmir = cast(
        'KMIR',
        SimpleNamespace(
            llvm_library_dir=None,
            definition_dir=Path('/tmp/definition'),
            definition=SimpleNamespace(main_module_name='KMIR-TEST'),
            bug_report=None,
        ),
    )
    proof = cast('APRProof', object())
    calls: list[tuple[str, dict[str, object]]] = []

    class FakeKoreServer:
        def __init__(self, args: dict[str, object]) -> None:
            calls.append(('kore', args))
            self.port = 31337

        def __enter__(self) -> FakeKoreServer:
            return self

        def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
            return None

    def fail_booster(*_args, **_kwargs) -> None:
        raise AssertionError('BoosterServer should not be used without llvm_library_dir')

    monkeypatch.setattr(_prove, 'KoreServer', FakeKoreServer)
    monkeypatch.setattr(_prove, 'BoosterServer', fail_booster)
    monkeypatch.setattr(_prove, 'parallel_advance_proof', lambda *_args, **_kwargs: None)

    _prove._prove_parallel(kmir, proof, opts=opts, label='demo', cut_point_rules=['rule'])

    assert calls == [
        (
            'kore',
            {
                'kompiled_dir': Path('/tmp/definition'),
                'module_name': 'KMIR-TEST',
                'bug_report': None,
                'haskell_threads': 2,
            },
        )
    ]
