from __future__ import annotations

import json
import os
import re
import shlex
from functools import lru_cache
from pathlib import Path
from typing import Final


REPO_ROOT: Final = Path(__file__).resolve().parents[4]
INTEGRATION_DATA_DIR: Final = (REPO_ROOT / 'kmir/src/tests/integration/data').resolve(strict=True)
MATRIX_PATH: Final = (REPO_ROOT / 'docs/coverage-matrix.json').resolve(strict=True)
COMPILE_FLAGS_LINE: Final = re.compile(r'^\s*//\s*@?\s*compile-flags:\s*(.+?)\s*$')
EDITION_LINE: Final = re.compile(r'^\s*//\s*@?\s*edition:\s*([0-9]{4})\s*$')


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


def external_max_depth(default: int = 500) -> int:
    raw = os.getenv('KMIR_EXTERNAL_MAX_DEPTH')
    if not raw:
        return default
    try:
        depth = int(raw)
    except ValueError:
        return default
    return depth if depth > 0 else default


def _sanitize_compile_flags(tokens: list[str]) -> list[str]:
    flags: list[str] = []
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        next_token = tokens[idx + 1] if idx + 1 < len(tokens) else None

        if token == '--edition' and next_token is not None:
            flags.append(f'--edition={next_token}')
            idx += 2
            continue
        if token in {'-C', '--C'} and next_token is not None:
            flags.append(f'-C{next_token}')
            idx += 2
            continue
        if token == '--crate-type' and next_token is not None:
            flags.append(f'--crate-type={next_token}')
            idx += 2
            continue
        if token == '-Z' and next_token is not None:
            if not next_token.startswith('miri-'):
                flags.append(f'-Z{next_token}')
            idx += 2
            continue

        if token.startswith('--edition='):
            flags.append(token)
        elif token.startswith('-C'):
            flags.append(token)
        elif token.startswith('--crate-type='):
            flags.append(token)
        elif token == '--test':
            flags.append(token)
        elif token.startswith('-Z') and not token.startswith('-Zmiri-'):
            flags.append(token)
        idx += 1

    deduped: list[str] = []
    seen: set[str] = set()
    for flag in flags:
        if flag not in seen:
            deduped.append(flag)
            seen.add(flag)
    return deduped


@lru_cache(maxsize=4096)
def external_rustc_flags(path: Path) -> tuple[str, ...]:
    source = path.read_text(errors='ignore')
    compile_tokens: list[str] = []
    explicit_edition: str | None = None

    for line in source.splitlines():
        match = EDITION_LINE.match(line)
        if match is not None:
            explicit_edition = match.group(1)

        match = COMPILE_FLAGS_LINE.match(line)
        if match is None:
            continue
        compile_tokens.extend(shlex.split(match.group(1)))

    flags = _sanitize_compile_flags(compile_tokens)
    if not any(flag.startswith('--edition=') for flag in flags):
        flags.insert(0, f'--edition={explicit_edition or "2021"}')
    return tuple(flags)
