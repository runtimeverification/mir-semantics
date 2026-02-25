from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final


REPO_ROOT: Final = Path(__file__).resolve().parents[4]
INTEGRATION_DATA_DIR: Final = (REPO_ROOT / 'kmir/src/tests/integration/data').resolve(strict=True)
MATRIX_PATH: Final = (REPO_ROOT / 'docs/coverage-matrix.json').resolve(strict=True)


def load_coverage_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text())


def suite_entries(matrix: dict, suite: str, bucket: str) -> set[str]:
    entries: set[str] = set()
    for section in matrix.get('sections', {}).values():
        entries.update(section.get(bucket, {}).get(suite, []))
    return entries


def suite_declared_entries(matrix: dict, suite: str) -> tuple[set[str], set[str]]:
    tests = suite_entries(matrix, suite, 'tests')
    skip = suite_entries(matrix, suite, 'skip')
    return tests, skip


def discover_suite_rs_files(suite: str) -> list[Path]:
    suite_dir = (INTEGRATION_DATA_DIR / suite).resolve()
    if not suite_dir.exists():
        return []
    return sorted(path for path in suite_dir.rglob('*.rs') if path.is_file())


def integration_data_relative(path: Path) -> str:
    return path.resolve().relative_to(INTEGRATION_DATA_DIR).as_posix()


def run_all_external_enabled() -> bool:
    value = os.getenv('KMIR_RUN_ALL_EXTERNAL', '')
    return value.lower() in {'1', 'true', 'yes', 'on'}


def external_max_depth(default: int = 200) -> int:
    raw = os.getenv('KMIR_EXTERNAL_MAX_DEPTH')
    if not raw:
        return default
    try:
        depth = int(raw)
    except ValueError:
        return default
    return depth if depth > 0 else default
