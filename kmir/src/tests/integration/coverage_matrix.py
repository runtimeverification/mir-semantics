from __future__ import annotations

import json
import os
import re
import shlex
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    import pytest


REPO_ROOT: Final = Path(__file__).resolve().parents[4]
INTEGRATION_DATA_DIR: Final = (REPO_ROOT / 'kmir/src/tests/integration/data').resolve()
MATRIX_PATH: Final = (REPO_ROOT / 'docs/coverage-matrix.json').resolve()

LOCAL_SUITES: Final = ('prove-rs', 'exec-smir', 'run-rs', 'ub')
EXTERNAL_SUITES: Final = ('miri-pass', 'miri-fail', 'ui-run-pass', 'kani', 'rustlantis')
COMPILE_FLAGS_LINE: Final = re.compile(r'^\s*//\s*@?\s*compile-flags:\s*(.+?)\s*$')
EDITION_LINE: Final = re.compile(r'^\s*//\s*@?\s*edition:\s*([0-9]{4})\s*$')
UI_DIRECTIVE_PREFIX: Final = re.compile(r'^\s*//@\s*(.+?)\s*$')
UI_REVISION_PREFIX: Final = re.compile(r'^\[([^\]]+)\](.*)$')
SUPPORTED_EDITIONS: Final = ('2015', '2018', '2021', '2024')

KANI_PROOF_ATTR_PATTERNS: Final = (
    re.compile(r'(?m)^\s*#\s*\[\s*kani::proof\s*\]\s*\n'),
    re.compile(r'(?m)^\s*#\s*\[\s*cfg_attr\s*\(\s*kani\s*,\s*kani::proof\s*\)\s*\]\s*\n'),
    re.compile(r'(?m)^\s*#\s*\[\s*kani::unwind\s*\([^\]]*\)\s*\]\s*\n'),
)


@dataclass(frozen=True)
class UIDirective:
    revision: str | None
    key: str
    value: str


@dataclass(frozen=True)
class UIAuxSpec:
    kind: str
    crate_name: str
    source_rel: str


@lru_cache(maxsize=1)
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


def suite_all_declared(matrix: dict, suite: str) -> set[str]:
    tests, skip = suite_declared_entries(matrix, suite)
    return tests | skip


def discover_suite_rs_files(suite: str) -> list[Path]:
    suite_dir = (INTEGRATION_DATA_DIR / suite).resolve()
    if not suite_dir.exists():
        return []
    return sorted(path for path in suite_dir.rglob('*.rs') if path.is_file())


def discover_suite_rs_rels(suite: str) -> list[str]:
    return [integration_data_relative(p) for p in discover_suite_rs_files(suite)]


@lru_cache(maxsize=8192)
def integration_data_relative(path: Path) -> str:
    return path.resolve().relative_to(INTEGRATION_DATA_DIR).as_posix()


def run_all_external_enabled() -> bool:
    value = os.getenv('KMIR_RUN_ALL_EXTERNAL', '')
    return value.lower() in {'1', 'true', 'yes', 'on'}


def external_kani_mode(default: str = 'deferred') -> str:
    value = os.getenv('KMIR_KANI_MODE', default).strip().lower()
    if value in {'deferred', 'adapted'}:
        return value
    return default


def external_max_depth(default: int = 500) -> int:
    raw = os.getenv('KMIR_EXTERNAL_MAX_DEPTH')
    if not raw:
        return default
    try:
        depth = int(raw)
    except ValueError:
        return default
    return depth if depth > 0 else default


def setup_external_suite(
    suite: str,
    missing_message: str,
) -> tuple[list[Path], set[str], set[str], int, list[str], list[pytest.MarkDecorator]]:
    import pytest

    rs_files = discover_suite_rs_files(suite)
    matrix = load_coverage_matrix()
    test_set, skip_set = suite_declared_entries(matrix, suite)
    max_depth = external_max_depth(default=500)
    undeclared = sorted(
        rel for path in rs_files if (rel := integration_data_relative(path)) not in test_set | skip_set
    )
    marks: list[pytest.MarkDecorator] = [pytest.mark.external_suite]
    if not rs_files:
        marks.append(pytest.mark.skip(reason=missing_message))
    return rs_files, test_set, skip_set, max_depth, undeclared, marks


def _sanitize_compile_flags(tokens: list[str]) -> list[str]:
    flags: list[str] = []
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        next_token = tokens[idx + 1] if idx + 1 < len(tokens) else None

        if token in {'--cfg', '--check-cfg', '--extern', '-L', '--emit', '--target', '--crate-name', '-A', '-D', '-F', '-W'} and next_token:
            flags.extend([token, next_token])
            idx += 2
            continue

        if token == '--edition' and next_token is not None:
            normalized = _normalize_edition(next_token)
            flags.append(f'--edition={normalized}')
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
            normalized = _normalize_edition(token.split('=', 1)[1])
            flags.append(f'--edition={normalized}')
        elif token.startswith('-C'):
            flags.append(token)
        elif token.startswith('--crate-type='):
            flags.append(token)
        elif token == '--test':
            flags.append(token)
        elif token.startswith('--cfg='):
            flags.append(token)
        elif token.startswith('--check-cfg='):
            flags.append(token)
        elif token.startswith('--extern='):
            flags.append(token)
        elif token.startswith('-L'):
            flags.append(token)
        elif token.startswith('--emit='):
            flags.append(token)
        elif token.startswith('--target='):
            flags.append(token)
        elif token.startswith('--crate-name='):
            flags.append(token)
        elif token.startswith('-A') or token.startswith('-D') or token.startswith('-F') or token.startswith('-W'):
            flags.append(token)
        elif token.startswith('-Z') and not token.startswith('-Zmiri-'):
            flags.append(token)
        elif token.startswith('-Zmiri-'):
            pass  # intentionally drop miri-specific flags
        else:
            flags.append(token)
        idx += 1

    return flags


def _normalize_edition(raw: str) -> str:
    value = raw.strip()
    if value in SUPPORTED_EDITIONS:
        return value

    if '..' in value:
        parts = [part.strip() for part in value.split('..') if part.strip()]
        for candidate in reversed(parts):
            if candidate in SUPPORTED_EDITIONS:
                return candidate
        for candidate in parts:
            if candidate in SUPPORTED_EDITIONS:
                return candidate

    for token in re.findall(r'\d{4}', value):
        if token in SUPPORTED_EDITIONS:
            return token

    return '2021'


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
        edition = _normalize_edition(explicit_edition or '2021')
        flags.insert(0, f'--edition={edition}')
    return tuple(flags)


def _parse_ui_directive_body(body: str) -> UIDirective | None:
    revision: str | None = None
    revision_match = UI_REVISION_PREFIX.match(body)
    if revision_match is not None:
        revision = revision_match.group(1).strip() or None
        body = revision_match.group(2).strip()

    if not body:
        return None

    if ':' in body:
        key, value = body.split(':', 1)
        return UIDirective(revision=revision, key=key.strip(), value=value.strip())

    parts = body.split(None, 1)
    key = parts[0].strip()
    value = parts[1].strip() if len(parts) == 2 else ''
    return UIDirective(revision=revision, key=key, value=value)


@lru_cache(maxsize=8192)
def ui_directives(path: Path) -> tuple[UIDirective, ...]:
    directives: list[UIDirective] = []
    for raw_line in path.read_text(errors='ignore').splitlines():
        match = UI_DIRECTIVE_PREFIX.match(raw_line)
        if match is None:
            continue
        directive = _parse_ui_directive_body(match.group(1).strip())
        if directive is None:
            continue
        directives.append(directive)
    return tuple(directives)


def ui_revisions(path: Path) -> tuple[str, ...]:
    revisions: list[str] = []
    for directive in ui_directives(path):
        if directive.key != 'revisions':
            continue
        for revision in directive.value.split():
            if revision and revision not in revisions:
                revisions.append(revision)
    return tuple(revisions)


def ui_active_revisions(path: Path) -> tuple[str | None, ...]:
    revisions = ui_revisions(path)
    run_pass_directives = [d for d in ui_directives(path) if d.key == 'run-pass']
    has_global_run_pass = any(d.revision is None for d in run_pass_directives)
    run_pass_revisions = {d.revision for d in run_pass_directives if d.revision is not None}

    if not revisions:
        return (None,) if has_global_run_pass else tuple()

    if run_pass_revisions:
        active = [revision for revision in revisions if revision in run_pass_revisions]
        return tuple(active)

    if has_global_run_pass:
        return tuple(revisions)

    return tuple()


def ui_case_directives(path: Path, revision: str | None) -> tuple[UIDirective, ...]:
    return tuple(d for d in ui_directives(path) if d.revision is None or d.revision == revision)


def ui_case_rustc_flags(path: Path, revision: str | None) -> tuple[str, ...]:
    compile_tokens: list[str] = []
    explicit_edition: str | None = None

    for directive in ui_case_directives(path, revision):
        if directive.key == 'edition' and directive.value:
            explicit_edition = _normalize_edition(directive.value.split()[0])
            continue
        if directive.key == 'compile-flags' and directive.value:
            compile_tokens.extend(shlex.split(directive.value))

    flags = _sanitize_compile_flags(compile_tokens)
    if not any(flag.startswith('--edition=') for flag in flags):
        edition = _normalize_edition(explicit_edition or '2021')
        flags.insert(0, f'--edition={edition}')
    return tuple(flags)


def ui_case_rustc_env(path: Path, revision: str | None) -> dict[str, str]:
    env: dict[str, str] = {}
    for directive in ui_case_directives(path, revision):
        if directive.key != 'rustc-env' or not directive.value or '=' not in directive.value:
            continue
        key, value = directive.value.split('=', 1)
        key = key.strip()
        if key:
            env[key] = value.strip()
    return env


def _sanitize_crate_name(value: str) -> str:
    return value.replace('-', '_').strip()


def ui_case_aux_specs(path: Path, revision: str | None) -> tuple[UIAuxSpec, ...]:
    specs: list[UIAuxSpec] = []
    for directive in ui_case_directives(path, revision):
        if directive.key == 'aux-build' and directive.value:
            src_rel = directive.value.strip()
            specs.append(UIAuxSpec('aux-build', _sanitize_crate_name(Path(src_rel).stem), src_rel))
            continue

        if directive.key == 'proc-macro' and directive.value:
            src_rel = directive.value.strip()
            specs.append(UIAuxSpec('proc-macro', _sanitize_crate_name(Path(src_rel).stem), src_rel))
            continue

        if directive.key == 'aux-crate' and directive.value:
            value = directive.value.strip()
            if '=' in value:
                crate_name, src_rel = value.split('=', 1)
                specs.append(UIAuxSpec('aux-crate', _sanitize_crate_name(crate_name), src_rel.strip()))
            else:
                specs.append(UIAuxSpec('aux-crate', _sanitize_crate_name(Path(value).stem), value))

    return tuple(specs)


def strip_kani_attributes(source: str) -> str:
    stripped = source
    for pattern in KANI_PROOF_ATTR_PATTERNS:
        stripped = pattern.sub('', stripped)
    return stripped


def kani_source_requires_runtime(source: str) -> bool:
    return 'kani::' in source


@lru_cache(maxsize=4096)
def adapted_kani_source(path: Path) -> str:
    source = path.read_text(errors='ignore')
    return strip_kani_attributes(source)
