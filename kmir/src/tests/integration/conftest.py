from __future__ import annotations

import hashlib
import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import TempPathFactory


def _smir_kompile_key(smir_json: Path, symbolic: bool) -> str:
    """Return a short stable key for a (smir_json, symbolic) pair."""
    path_hash = hashlib.sha256(str(smir_json).encode()).hexdigest()[:16]
    suffix = 'symbolic' if symbolic else 'concrete'
    return f'{path_hash}-{suffix}'


@pytest.fixture(scope='session')
def kompile_cache_dir(tmp_path_factory: TempPathFactory) -> Path:
    """Session-scoped base directory for kompile cache.

    Returns a stable temporary directory that persists across the test session,
    allowing KompileDigest caching in kompile_smir to avoid redundant llvm-kompile calls
    when multiple test_exec_smir parametrizations share the same smir_json + symbolic combo.
    """
    return tmp_path_factory.mktemp('kompile-cache', numbered=False)


@pytest.fixture(scope='session')
def exec_smir_kompile_dirs(kompile_cache_dir: Path) -> dict[str, Path]:
    """Session-scoped mapping from (smir_json, symbolic) key to shared kompile output dir.

    Multiple test_exec_smir invocations that share the same smir_json + symbolic flag
    will reuse the same target_dir, letting KompileDigest skip redundant kompile calls.
    """
    return {}


def get_exec_smir_target_dir(
    smir_json: Path,
    symbolic: bool,
    kompile_cache_dir: Path,
    exec_smir_kompile_dirs: dict[str, Path],
) -> Path:
    """Return a shared target directory for a given (smir_json, symbolic) pair.

    Uses a file lock to avoid concurrent kompile races when running under pytest-xdist.
    """
    key = _smir_kompile_key(smir_json, symbolic)
    if key in exec_smir_kompile_dirs:
        return exec_smir_kompile_dirs[key]

    target = kompile_cache_dir / key
    lock_file = kompile_cache_dir / f'{key}.lock'

    try:
        # Attempt to claim the lock (atomic create)
        with open(lock_file, 'x'):
            target.mkdir(parents=True, exist_ok=True)
            exec_smir_kompile_dirs[key] = target
        lock_file.unlink(missing_ok=True)
    except FileExistsError:
        # Another worker is building; wait for the lock to be released (max 5 min)
        target.mkdir(parents=True, exist_ok=True)
        secs = 0
        while lock_file.exists() and secs < 300:
            time.sleep(1)
            secs += 1
        exec_smir_kompile_dirs[key] = target

    return target
