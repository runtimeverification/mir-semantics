from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from kmir.kmir import KMIR

PROVING_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)
PROVING_FILES = list(PROVING_DIR.glob('*.rs'))


@pytest.mark.parametrize(
    'rs_file',
    PROVING_FILES,
    ids=[spec.stem for spec in PROVING_FILES],
)
def test_prove_rs(rs_file: Path, kmir: KMIR) -> None:
    should_fail = rs_file.stem.endswith('fail')
    apr_proof = kmir.prove_rs(rs_file)
    if not should_fail:
        assert apr_proof.passed
    else:
        assert apr_proof.failed
