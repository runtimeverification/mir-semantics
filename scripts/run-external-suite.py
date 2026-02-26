#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DATA_DIR = REPO_ROOT / 'kmir/src/tests/integration/data'
MATRIX_PATH = REPO_ROOT / 'docs/coverage-matrix.json'
INTEGRATION_HELPERS_DIR = REPO_ROOT / 'kmir/src/tests/integration'

if str(INTEGRATION_HELPERS_DIR) not in sys.path:
    sys.path.insert(0, str(INTEGRATION_HELPERS_DIR))

from coverage_matrix import (  # noqa: E402
    adapted_kani_source,
    external_kani_mode,
    external_rustc_flags,
    kani_source_requires_runtime,
    ui_active_revisions,
    ui_case_aux_specs,
    ui_case_directives,
    ui_case_rustc_env,
    ui_case_rustc_flags,
)

STATUS_RE = re.compile(r'status:\s*ProofStatus\.([A-Z_]+)')
ERROR_CODE_RE = re.compile(r'error\[(E\d{4})\]')

SUITE_EXPECTED_STATUS = {
    'miri-pass': 'PASSED',
    'miri-fail': 'FAILED',
    'ui-run-pass': 'PASSED',
    'kani': 'PASSED',
    'rustlantis': 'PASSED',
}

SUITE_REQUIRE_LINEAR_CHAIN = {
    'miri-pass': True,
    'miri-fail': False,
    'ui-run-pass': True,
    'kani': True,
    'rustlantis': True,
}


@dataclass(frozen=True)
class PreparedCase:
    rel: str
    case_id: str
    source_path: Path
    expected_status: str
    require_linear: bool
    rustc_flags: tuple[str, ...]
    env_overrides: dict[str, str]
    ui_revision: str | None = None
    ui_aux_specs: tuple = ()
    source_override: str | None = None
    pre_outcome: str | None = None
    pre_reason: str | None = None
    pre_detail: str | None = None


@dataclass
class CaseResult:
    rel: str
    case_id: str
    outcome: str
    status: str | None
    returncode: int | None
    duration_s: float
    linear_chain: bool
    reason: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run external suite samples via direct `kmir prove-rs` and emit per-file outcomes.'
    )
    parser.add_argument('--suite', choices=sorted(SUITE_EXPECTED_STATUS), required=True, help='External suite to run.')
    parser.add_argument('--out', type=Path, required=True, help='Output JSON path.')
    parser.add_argument('--max-depth', type=int, default=500, help='max_depth for `kmir prove-rs` (default: 500).')
    parser.add_argument('--workers', type=int, default=1, help='Parallel worker count (default: 1).')
    parser.add_argument('--case-timeout', type=int, default=0, help='Per-case timeout in seconds (0 disables timeout).')
    parser.add_argument(
        '--progress-every',
        type=int,
        default=25,
        help='Print one progress line every N completed samples (default: 25).',
    )
    parser.add_argument(
        '--proof-root',
        type=Path,
        default=Path('/tmp/kmir-proof-suites'),
        help='Root directory for generated proof artifacts.',
    )
    parser.add_argument(
        '--mode',
        choices=('prove-rs', 'batch', 'isolated'),
        default='prove-rs',
        help='Compatibility alias: all modes execute direct prove-rs now.',
    )
    parser.add_argument(
        '--numprocesses',
        type=int,
        default=0,
        help='Compatibility no-op flag.',
    )
    parser.add_argument(
        '--match',
        type=str,
        default='',
        help='Optional regex filter applied to suite-relative case paths.',
    )
    parser.add_argument(
        '--kani-mode',
        choices=('deferred', 'adapted'),
        default=external_kani_mode(),
        help='Kani execution mode (default from KMIR_KANI_MODE env, fallback deferred).',
    )
    return parser.parse_args()


def discover_suite_rs_files(suite: str) -> list[str]:
    suite_dir = INTEGRATION_DATA_DIR / suite
    if not suite_dir.exists():
        return []
    return sorted(path.relative_to(INTEGRATION_DATA_DIR).as_posix() for path in suite_dir.rglob('*.rs') if path.is_file())


def _suite_declared_entries(matrix: dict, suite: str) -> set[str]:
    declared: set[str] = set()
    for section in matrix.get('sections', {}).values():
        declared.update(section.get('tests', {}).get(suite, []))
        declared.update(section.get('skip', {}).get(suite, []))
    return declared


def _status_from_output(output: str) -> str | None:
    match = STATUS_RE.search(output)
    return match.group(1) if match else None


def _first_error_code(output: str) -> str | None:
    match = ERROR_CODE_RE.search(output)
    return match.group(1) if match else None


def _detail_from_output(output: str, fallback: str) -> str:
    code = _first_error_code(output)
    if code is not None:
        return code
    for line in output.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:240]
    return fallback


def _proof_linear_chain(proof_base: Path, proof_id: str) -> bool:
    proof_path = proof_base / proof_id / 'proof.json'
    kcfg_path = proof_base / proof_id / 'kcfg' / 'kcfg.json'
    if not proof_path.exists() or not kcfg_path.exists():
        return False

    proof = json.loads(proof_path.read_text())
    kcfg = json.loads(kcfg_path.read_text())

    target = proof.get('target')
    nodes = kcfg.get('nodes', [])
    if not isinstance(target, int) or not isinstance(nodes, list) or target not in nodes:
        return False

    ins: dict[int, int] = defaultdict(int)
    outs: dict[int, int] = defaultdict(int)

    for edge_kind in ('edges', 'covers'):
        for edge in kcfg.get(edge_kind, []):
            if not isinstance(edge, dict):
                return False
            src = edge.get('source')
            dst = edge.get('target')
            if not isinstance(src, int) or not isinstance(dst, int):
                return False
            outs[src] += 1
            ins[dst] += 1

    if any(outs[node] > 1 for node in nodes):
        return False
    if any(ins[node] > 1 for node in nodes):
        return False

    roots = [node for node in nodes if ins[node] == 0]
    if len(roots) != 1:
        return False

    return outs[target] == 0


def _kill_process_group(proc: subprocess.Popen[str]) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _run_command(
    cmd: list[str],
    *,
    env: dict[str, str],
    cwd: Path,
    timeout_s: int | None,
) -> tuple[bool, int | None, str, float]:
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    timed_out = False
    try:
        output, _ = proc.communicate(timeout=timeout_s)
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process_group(proc)
        output, _ = proc.communicate()
        returncode = None

    elapsed = time.monotonic() - start
    return timed_out, returncode, output or '', elapsed


def _resolve_relative_path(raw: str, base_dir: Path) -> str:
    value = raw.strip()
    if not value:
        return raw

    if value.startswith('@') and len(value) > 1:
        return f'@{_resolve_relative_path(value[1:], base_dir)}'

    if value.startswith('$'):
        return raw

    path = Path(value)
    if path.is_absolute():
        return value

    return str((base_dir / path).resolve())


def _normalize_search_path(raw: str, base_dir: Path) -> str:
    value = raw.strip()
    if not value:
        return raw

    if '=' in value:
        prefix, suffix = value.split('=', 1)
        if re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', prefix):
            return f'{prefix}={_resolve_relative_path(suffix, base_dir)}'

    return _resolve_relative_path(value, base_dir)


def _normalize_extern(raw: str, base_dir: Path) -> str:
    value = raw.strip()
    if not value or '=' not in value:
        return raw

    crate_name, artifact = value.split('=', 1)
    if not crate_name or not artifact:
        return raw

    return f'{crate_name}={_resolve_relative_path(artifact, base_dir)}'


def _normalize_rustc_flags(flags: tuple[str, ...], base_dir: Path) -> tuple[str, ...]:
    normalized: list[str] = []
    idx = 0

    while idx < len(flags):
        token = flags[idx]
        next_token = flags[idx + 1] if idx + 1 < len(flags) else None

        if token == '-L' and next_token is not None:
            normalized.extend(['-L', _normalize_search_path(next_token, base_dir)])
            idx += 2
            continue

        if token.startswith('-L') and token != '-L':
            normalized.append(f'-L{_normalize_search_path(token[2:], base_dir)}')
            idx += 1
            continue

        if token == '--extern' and next_token is not None:
            normalized.extend(['--extern', _normalize_extern(next_token, base_dir)])
            idx += 2
            continue

        if token.startswith('--extern='):
            normalized.append(f'--extern={_normalize_extern(token.split("=", 1)[1], base_dir)}')
            idx += 1
            continue

        if token in {'--out-dir', '--sysroot', '--target-dir'} and next_token is not None:
            normalized.extend([token, _resolve_relative_path(next_token, base_dir)])
            idx += 2
            continue

        normalized.append(token)
        idx += 1

    return tuple(normalized)


def _stable_mir_json_executable() -> Path | None:
    candidates = [
        REPO_ROOT / 'deps/.stable-mir-json/release.sh',
        REPO_ROOT / 'deps/.stable-mir-json/debug.sh',
    ]

    on_path = shutil.which('stable_mir_json')
    if on_path is not None:
        candidates.append(Path(on_path))

    candidates.extend(
        [
            Path.home() / '.stable-mir-json/release.sh',
            Path.home() / '.stable-mir-json/debug.sh',
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def _host_triple() -> str:
    try:
        proc = subprocess.run(
            ['rustc', '-vV'],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
    except OSError:
        proc = None

    if proc is not None and proc.returncode == 0:
        for line in proc.stdout.splitlines():
            if line.startswith('host:'):
                return line.split(':', 1)[1].strip().lower()

    machine = platform.machine().lower() or 'unknown'
    system = platform.system().lower() or 'unknown'
    return f'{machine}-unknown-{system}'


def _host_matches_tag(tag: str, host_triple: str) -> bool:
    normalized = tag.strip().lower().replace('_', '-')
    if not normalized:
        return False

    if normalized in host_triple:
        return True

    alias_checks = {
        'apple': ('apple', 'darwin'),
        'linux': ('linux',),
        'windows': ('windows',),
        'x86-64': ('x86_64', 'amd64'),
        'x86_64': ('x86_64', 'amd64'),
        'arm': ('arm', 'aarch64'),
        'thumb': ('thumb',),
        'musl': ('musl',),
        'gnu': ('gnu',),
        'android': ('android',),
        'wasm': ('wasm',),
        'emscripten': ('emscripten',),
        'fuchsia': ('fuchsia',),
    }

    candidates = alias_checks.get(normalized)
    if candidates is None:
        return normalized in host_triple
    return any(candidate in host_triple for candidate in candidates)


def _ui_platform_skip_reason(rel: str, revision: str | None, host_triple: str) -> tuple[str | None, str | None]:
    src_path = INTEGRATION_DATA_DIR / rel
    for directive in ui_case_directives(src_path, revision):
        key = directive.key.strip().lower()
        if key.startswith('only-'):
            tag = key.removeprefix('only-')
            if not _host_matches_tag(tag, host_triple):
                return 'policy_skip', f'platform-only:{key}'
            continue

        if key.startswith('ignore-'):
            tag = key.removeprefix('ignore-')
            if _host_matches_tag(tag, host_triple):
                return 'policy_skip', f'platform-ignore:{key}'
            continue

        if key == 'ignore-backends' and 'kmir' in directive.value.lower().split():
            return 'policy_skip', 'backend-ignore:kmir'

    return None, None


def _resolve_ui_aux_source(test_source: Path, source_rel: str) -> Path | None:
    source_rel = source_rel.strip()
    if not source_rel:
        return None

    candidates = [
        test_source.parent / source_rel,
        test_source.parent / 'auxiliary' / source_rel,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


def _find_aux_artifact(aux_out_dir: Path, crate_name: str, kind: str) -> Path | None:
    prefix = f'lib{crate_name}'
    matches = sorted(path for path in aux_out_dir.iterdir() if path.is_file() and path.name.startswith(prefix))
    if not matches:
        return None

    if kind == 'proc-macro':
        for path in matches:
            if path.suffix in {'.so', '.dylib', '.dll'}:
                return path

    for path in matches:
        if path.suffix == '.rlib':
            return path

    return matches[0]


def _find_aux_artifact_from_new_files(new_files: list[Path], kind: str) -> Path | None:
    if not new_files:
        return None

    files = [path for path in new_files if path.is_file()]
    if not files:
        return None

    if kind == 'proc-macro':
        for path in files:
            if path.suffix in {'.so', '.dylib', '.dll'}:
                return path

    for path in files:
        if path.suffix == '.rlib':
            return path

    for path in files:
        if path.suffix in {'.so', '.dylib', '.dll'}:
            return path

    return files[0]


def _compile_ui_aux(
    case: PreparedCase,
    *,
    case_root: Path,
    env: dict[str, str],
    timeout_s: int | None,
) -> tuple[tuple[str, ...], str | None, str]:
    if not case.ui_aux_specs:
        return tuple(), None, ''

    aux_out_dir = case_root / 'aux'
    aux_out_dir.mkdir(parents=True, exist_ok=True)

    externs: dict[str, Path] = {}

    for spec in case.ui_aux_specs:
        source = _resolve_ui_aux_source(case.source_path, spec.source_rel)
        if source is None:
            return tuple(), 'prep_failed', f'aux-missing:{spec.source_rel}'

        aux_flags = list(_normalize_rustc_flags(ui_case_rustc_flags(source, None), source.parent))

        if not any(flag.startswith('--crate-type=') for flag in aux_flags):
            crate_type = 'proc-macro' if spec.kind == 'proc-macro' else 'rlib'
            aux_flags.append(f'--crate-type={crate_type}')

        before_files = {path.resolve() for path in aux_out_dir.iterdir()}
        cmd = ['rustc', *aux_flags, '--out-dir', str(aux_out_dir), str(source)]
        cmd.extend(['-L', f'dependency={aux_out_dir}'])
        for crate_name, artifact in externs.items():
            cmd.extend(['--extern', f'{crate_name}={artifact}'])

        timed_out, returncode, output, _ = _run_command(
            cmd,
            env=env,
            cwd=REPO_ROOT,
            timeout_s=timeout_s,
        )

        if timed_out:
            return tuple(), 'timeout', f'aux-timeout:{spec.source_rel}'

        if returncode != 0:
            detail = _detail_from_output(output, f'aux-compile-failed:{spec.source_rel}')
            return tuple(), 'compile_failed', f'aux:{detail}'

        after_files = {path.resolve() for path in aux_out_dir.iterdir()}
        new_files = sorted(after_files - before_files)
        artifact = _find_aux_artifact_from_new_files(new_files, spec.kind)
        if artifact is None:
            artifact = _find_aux_artifact(aux_out_dir, spec.crate_name, spec.kind)
        if artifact is None:
            return tuple(), 'prep_failed', f'aux-artifact-missing:{spec.crate_name}'

        externs[spec.crate_name] = artifact

    extra_flags: list[str] = ['-L', f'dependency={aux_out_dir}']
    for crate_name, artifact in externs.items():
        extra_flags.extend(['--extern', f'{crate_name}={artifact}'])
    return tuple(extra_flags), None, ''


def _compile_probe(
    source_path: Path,
    *,
    rustc_flags: tuple[str, ...],
    probe_dir: Path,
    env: dict[str, str],
    timeout_s: int | None,
) -> tuple[str | None, str]:
    stable_mir_json = _stable_mir_json_executable()
    if stable_mir_json is None:
        return 'prep_failed', 'stable_mir_json_not_found'

    probe_dir.mkdir(parents=True, exist_ok=True)
    cmd = [str(stable_mir_json), '-Zno-codegen', '--out-dir', str(probe_dir), *rustc_flags, str(source_path)]

    timed_out, returncode, output, _ = _run_command(
        cmd,
        env=env,
        cwd=REPO_ROOT,
        timeout_s=timeout_s,
    )

    if timed_out:
        return 'timeout', 'compile-timeout'

    if returncode != 0:
        return 'compile_failed', _detail_from_output(output, 'compile_failed')

    return None, ''


def _prepare_default_cases(suite: str, discovered: list[str]) -> tuple[list[PreparedCase], dict[str, list[str]]]:
    prepared: list[PreparedCase] = []
    parent_map: dict[str, list[str]] = {}

    for rel in discovered:
        path = INTEGRATION_DATA_DIR / rel
        case_id = rel
        case = PreparedCase(
            rel=rel,
            case_id=case_id,
            source_path=path,
            expected_status=SUITE_EXPECTED_STATUS[suite],
            require_linear=SUITE_REQUIRE_LINEAR_CHAIN[suite],
            rustc_flags=external_rustc_flags(path),
            env_overrides={},
        )
        prepared.append(case)
        parent_map[rel] = [case_id]

    return prepared, parent_map


def _prepare_ui_cases(discovered: list[str], host_triple: str) -> tuple[list[PreparedCase], dict[str, list[str]]]:
    prepared: list[PreparedCase] = []
    parent_map: dict[str, list[str]] = {}

    for rel in discovered:
        path = INTEGRATION_DATA_DIR / rel
        case_ids: list[str] = []
        revisions = ui_active_revisions(path)
        if not revisions:
            case = PreparedCase(
                rel=rel,
                case_id=rel,
                source_path=path,
                expected_status='PASSED',
                require_linear=True,
                rustc_flags=external_rustc_flags(path),
                env_overrides={},
                pre_outcome='skipped',
                pre_reason='policy_skip',
                pre_detail='not-run-pass',
            )
            prepared.append(case)
            case_ids.append(case.case_id)
            parent_map[rel] = case_ids
            continue

        for revision in revisions:
            case_id = f'{rel}@{revision}' if revision is not None else rel
            skip_reason, skip_detail = _ui_platform_skip_reason(rel, revision, host_triple)
            case = PreparedCase(
                rel=rel,
                case_id=case_id,
                source_path=path,
                expected_status='PASSED',
                require_linear=True,
                rustc_flags=ui_case_rustc_flags(path, revision),
                env_overrides=ui_case_rustc_env(path, revision),
                ui_revision=revision,
                ui_aux_specs=ui_case_aux_specs(path, revision),
                pre_outcome='skipped' if skip_reason is not None else None,
                pre_reason=skip_reason,
                pre_detail=skip_detail,
            )
            prepared.append(case)
            case_ids.append(case_id)

        parent_map[rel] = case_ids

    return prepared, parent_map


def _prepare_kani_cases(discovered: list[str], mode: str) -> tuple[list[PreparedCase], dict[str, list[str]]]:
    prepared: list[PreparedCase] = []
    parent_map: dict[str, list[str]] = {}

    for rel in discovered:
        path = INTEGRATION_DATA_DIR / rel
        case_id = rel

        if mode == 'deferred':
            case = PreparedCase(
                rel=rel,
                case_id=case_id,
                source_path=path,
                expected_status='PASSED',
                require_linear=True,
                rustc_flags=external_rustc_flags(path),
                env_overrides={},
                pre_outcome='skipped',
                pre_reason='policy_skip',
                pre_detail='kani-deferred-not-in-scope',
            )
            prepared.append(case)
            parent_map[rel] = [case_id]
            continue

        adapted_source = adapted_kani_source(path)
        if kani_source_requires_runtime(adapted_source):
            case = PreparedCase(
                rel=rel,
                case_id=case_id,
                source_path=path,
                expected_status='PASSED',
                require_linear=True,
                rustc_flags=external_rustc_flags(path),
                env_overrides={},
                pre_outcome='skipped',
                pre_reason='policy_skip',
                pre_detail='kani-runtime-required',
            )
        else:
            case = PreparedCase(
                rel=rel,
                case_id=case_id,
                source_path=path,
                expected_status='PASSED',
                require_linear=True,
                rustc_flags=external_rustc_flags(path),
                env_overrides={},
                source_override=adapted_source,
            )

        prepared.append(case)
        parent_map[rel] = [case_id]

    return prepared, parent_map


def _prepare_cases(args: argparse.Namespace, discovered: list[str]) -> tuple[list[PreparedCase], dict[str, list[str]], dict]:
    host_triple = _host_triple()
    metadata = {
        'host_triple': host_triple,
        'kani_mode': args.kani_mode if args.suite == 'kani' else None,
    }

    if args.suite == 'ui-run-pass':
        cases, parent_map = _prepare_ui_cases(discovered, host_triple)
        return cases, parent_map, metadata

    if args.suite == 'kani':
        cases, parent_map = _prepare_kani_cases(discovered, args.kani_mode)
        return cases, parent_map, metadata

    cases, parent_map = _prepare_default_cases(args.suite, discovered)
    return cases, parent_map, metadata


def _run_prepared_case(case: PreparedCase, args: argparse.Namespace) -> CaseResult:
    if case.pre_outcome is not None:
        return CaseResult(
            rel=case.rel,
            case_id=case.case_id,
            outcome=case.pre_outcome,
            status=None,
            returncode=0,
            duration_s=0.0,
            linear_chain=False,
            reason=case.pre_reason or 'policy_skip',
            detail=case.pre_detail or 'pre-filtered',
        )

    case_key = hashlib.sha1(case.case_id.encode()).hexdigest()[:12]
    case_root = args.proof_root / args.suite / f'{Path(case.rel).stem}-{case_key}'

    if case_root.exists():
        subprocess.run(['rm', '-rf', str(case_root)], check=True)
    case_root.mkdir(parents=True, exist_ok=True)

    source_to_prove = case.source_path
    if case.source_override is not None:
        source_to_prove = case_root / f'{case.source_path.stem}_adapted.rs'
        source_to_prove.write_text(case.source_override)

    rustc_flags = list(_normalize_rustc_flags(case.rustc_flags, case.source_path.parent))
    env = os.environ.copy()
    env.update(case.env_overrides)

    timeout_s = args.case_timeout if args.case_timeout > 0 else None
    compile_timeout = min(timeout_s, 120) if timeout_s is not None else 120

    if args.suite == 'ui-run-pass' and case.ui_aux_specs:
        extra_flags, prep_reason, prep_detail = _compile_ui_aux(
            case,
            case_root=case_root,
            env=env,
            timeout_s=compile_timeout,
        )
        if prep_reason is not None:
            return CaseResult(
                rel=case.rel,
                case_id=case.case_id,
                outcome='failed',
                status=None,
                returncode=1,
                duration_s=0.0,
                linear_chain=False,
                reason=prep_reason,
                detail=prep_detail,
            )
        rustc_flags.extend(extra_flags)

    probe_reason, probe_detail = _compile_probe(
        source_to_prove,
        rustc_flags=tuple(rustc_flags),
        probe_dir=case_root / 'compile-probe',
        env=env,
        timeout_s=compile_timeout,
    )
    if probe_reason is not None:
        outcome = 'skipped' if probe_reason == 'policy_skip' else 'failed'
        return CaseResult(
            rel=case.rel,
            case_id=case.case_id,
            outcome=outcome,
            status=None,
            returncode=1,
            duration_s=0.0,
            linear_chain=False,
            reason=probe_reason,
            detail=probe_detail,
        )

    env['KMIR_EXTRA_RUSTC_FLAGS'] = ' '.join(rustc_flags)

    cmd = [
        'uv',
        '--project',
        'kmir',
        'run',
        '--python',
        'cpython-3.11.13',
        'kmir',
        'prove-rs',
        str(source_to_prove),
        '--max-depth',
        str(args.max_depth),
        '--proof-dir',
        str(case_root),
        '--reload',
    ]

    timed_out, returncode, output, duration_s = _run_command(
        cmd,
        env=env,
        cwd=REPO_ROOT,
        timeout_s=timeout_s,
    )

    status = _status_from_output(output)
    proof_id = f'{source_to_prove.stem}.main'
    linear_chain = _proof_linear_chain(case_root, proof_id)

    if timed_out:
        return CaseResult(
            rel=case.rel,
            case_id=case.case_id,
            outcome='failed',
            status=status,
            returncode=returncode,
            duration_s=duration_s,
            linear_chain=linear_chain,
            reason='timeout',
            detail='prove-timeout',
        )

    if status is None:
        return CaseResult(
            rel=case.rel,
            case_id=case.case_id,
            outcome='failed',
            status=status,
            returncode=returncode,
            duration_s=duration_s,
            linear_chain=linear_chain,
            reason='proof_failed',
            detail=_detail_from_output(output, 'missing-status'),
        )

    if status != case.expected_status:
        return CaseResult(
            rel=case.rel,
            case_id=case.case_id,
            outcome='failed',
            status=status,
            returncode=returncode,
            duration_s=duration_s,
            linear_chain=linear_chain,
            reason='proof_failed',
            detail=f'status={status}',
        )

    if case.require_linear and not linear_chain:
        return CaseResult(
            rel=case.rel,
            case_id=case.case_id,
            outcome='failed',
            status=status,
            returncode=returncode,
            duration_s=duration_s,
            linear_chain=linear_chain,
            reason='non_linear_proof',
            detail='proof-graph-not-linear',
        )

    return CaseResult(
        rel=case.rel,
        case_id=case.case_id,
        outcome='passed',
        status=status,
        returncode=returncode,
        duration_s=duration_s,
        linear_chain=linear_chain,
        reason='passed',
        detail='ok',
    )


def _aggregate_parent_results(
    parent_map: dict[str, list[str]],
    case_results: dict[str, CaseResult],
) -> tuple[dict[str, str], dict[str, dict], list[dict[str, str | int | float | None]]]:
    final_results: dict[str, str] = {}
    parent_details: dict[str, dict] = {}
    sample_non_pass: list[dict[str, str | int | float | None]] = []

    for rel in sorted(parent_map):
        subcases = [case_results[case_id] for case_id in parent_map[rel]]
        failed = [case for case in subcases if case.outcome == 'failed']
        passed = [case for case in subcases if case.outcome == 'passed']
        skipped = [case for case in subcases if case.outcome == 'skipped']

        if failed:
            selected = failed[0]
            outcome = 'failed'
        elif passed:
            selected = passed[0]
            outcome = 'passed'
        elif skipped:
            selected = skipped[0]
            outcome = 'skipped'
        else:
            selected = subcases[0]
            outcome = selected.outcome

        final_results[rel] = outcome
        parent_details[rel] = {
            'reason': selected.reason,
            'detail': selected.detail,
            'status': selected.status,
            'returncode': selected.returncode,
            'duration_seconds': round(sum(case.duration_s for case in subcases), 3),
            'linear_chain': selected.linear_chain,
            'subcases': [case.case_id for case in subcases],
        }

        if outcome != 'passed' and len(sample_non_pass) < 40:
            sample_non_pass.append(
                {
                    'path': rel,
                    'reason': selected.reason,
                    'detail': selected.detail,
                    'status': selected.status,
                    'returncode': selected.returncode,
                    'duration_seconds': parent_details[rel]['duration_seconds'],
                    'linear_chain': selected.linear_chain,
                }
            )

    return final_results, parent_details, sample_non_pass


def main() -> int:
    args = parse_args()
    if args.max_depth <= 0:
        raise ValueError('--max-depth must be > 0')
    if args.workers <= 0:
        raise ValueError('--workers must be > 0')
    if args.progress_every <= 0:
        raise ValueError('--progress-every must be > 0')

    discovered = discover_suite_rs_files(args.suite)
    if args.match:
        matcher = re.compile(args.match)
        discovered = [rel for rel in discovered if matcher.search(rel)]

    if not discovered:
        print(f'No .rs files discovered for suite {args.suite}', file=sys.stderr)
        return 1

    matrix = json.loads(MATRIX_PATH.read_text())
    declared = _suite_declared_entries(matrix, args.suite)
    undeclared = sorted(set(discovered) - declared)
    if undeclared:
        print(
            f'Matrix alignment failed for {args.suite}: {len(undeclared)} undeclared files; first 20: {undeclared[:20]}',
            file=sys.stderr,
        )
        return 2

    args.proof_root = args.proof_root.resolve()
    args.proof_root.mkdir(parents=True, exist_ok=True)

    cases, parent_map, metadata = _prepare_cases(args, discovered)

    started = time.monotonic()
    case_results: dict[str, CaseResult] = {}
    completed = 0
    total = len(cases)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_run_prepared_case, case, args): case.case_id for case in cases}
        for future in as_completed(futures):
            completed += 1
            case = future.result()
            case_results[case.case_id] = case

            if completed % args.progress_every == 0 or case.outcome != 'passed':
                print(
                    f'[{completed}/{total}] {case.case_id}: {case.outcome} '
                    f'(status={case.status}, linear={case.linear_chain}, reason={case.reason}, detail={case.detail}, '
                    f'{case.duration_s:.1f}s)'
                )

    results, result_details, sample_non_pass = _aggregate_parent_results(parent_map, case_results)

    counts = {'passed': 0, 'failed': 0, 'skipped': 0, 'error': 0, 'xfailed': 0, 'notrun': 0}
    for outcome in results.values():
        counts[outcome] += 1

    reason_histogram = Counter(detail['reason'] for detail in result_details.values())
    detail_histogram = Counter(detail['detail'] for detail in result_details.values())

    elapsed_s = time.monotonic() - started

    payload = {
        'suite': args.suite,
        'mode': 'prove-rs',
        'max_depth': args.max_depth,
        'workers': args.workers,
        'case_timeout': args.case_timeout,
        'elapsed_seconds': round(elapsed_s, 3),
        'pytest_exit_code': 0 if counts['failed'] == 0 else 1,
        'counts': counts,
        'results': results,
        'result_details': result_details,
        'reason_histogram': dict(sorted(reason_histogram.items())),
        'detail_histogram': dict(sorted(detail_histogram.items())),
        'sample_failures': sample_non_pass,
        'metadata': metadata,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + '\n')

    print(
        f"{args.suite}: total={len(results)} passed={counts['passed']} failed={counts['failed']} "
        f"skipped={counts['skipped']} elapsed={elapsed_s:.1f}s"
    )
    print(f'Reasons: {dict(sorted(reason_histogram.items()))}')
    print(f'Wrote result file: {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
