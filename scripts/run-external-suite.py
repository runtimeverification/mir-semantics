#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DATA_DIR = REPO_ROOT / 'kmir/src/tests/integration/data'
MATRIX_PATH = REPO_ROOT / 'docs/coverage-matrix.json'

STATUS_RE = re.compile(r'status:\s*ProofStatus\.([A-Z_]+)')
COMPILE_FLAGS_LINE = re.compile(r'^\s*//\s*@?\s*compile-flags:\s*(.+?)\s*$')
EDITION_LINE = re.compile(r'^\s*//\s*@?\s*edition:\s*([0-9]{4})\s*$')

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


@dataclass
class CaseResult:
    rel: str
    outcome: str
    status: str | None
    returncode: int | None
    duration_s: float
    linear_chain: bool
    reason: str


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


def _sanitize_compile_flags(tokens: list[str]) -> list[str]:
    flags: list[str] = []
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        nxt = tokens[idx + 1] if idx + 1 < len(tokens) else None

        if token == '--edition' and nxt is not None:
            flags.append(f'--edition={nxt}')
            idx += 2
            continue
        if token in {'-C', '--C'} and nxt is not None:
            flags.append(f'-C{nxt}')
            idx += 2
            continue
        if token == '--crate-type' and nxt is not None:
            flags.append(f'--crate-type={nxt}')
            idx += 2
            continue
        if token == '-Z' and nxt is not None:
            if not nxt.startswith('miri-'):
                flags.append(f'-Z{nxt}')
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


def rustc_flags_for_file(path: Path) -> tuple[str, ...]:
    source = path.read_text(errors='ignore')
    compile_tokens: list[str] = []
    explicit_edition: str | None = None

    for line in source.splitlines():
        edition_match = EDITION_LINE.match(line)
        if edition_match is not None:
            explicit_edition = edition_match.group(1)

        compile_match = COMPILE_FLAGS_LINE.match(line)
        if compile_match is not None:
            compile_tokens.extend(shlex.split(compile_match.group(1)))

    flags = _sanitize_compile_flags(compile_tokens)
    if not any(flag.startswith('--edition=') for flag in flags):
        flags.insert(0, f'--edition={explicit_edition or "2021"}')
    return tuple(flags)


def _status_from_output(output: str) -> str | None:
    match = STATUS_RE.search(output)
    return match.group(1) if match else None


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

    for edge in kcfg.get('edges', []):
        if not isinstance(edge, dict):
            return False
        src = edge.get('source')
        dst = edge.get('target')
        if not isinstance(src, int) or not isinstance(dst, int):
            return False
        outs[src] += 1
        ins[dst] += 1

    for cover in kcfg.get('covers', []):
        if not isinstance(cover, dict):
            return False
        src = cover.get('source')
        dst = cover.get('target')
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

    if outs[target] != 0:
        return False

    return True


def _kill_process_group(proc: subprocess.Popen[str]) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_case(suite: str, rel: str, args: argparse.Namespace) -> CaseResult:
    rs_path = INTEGRATION_DATA_DIR / rel
    case_key = hashlib.sha1(rel.encode()).hexdigest()[:12]
    case_root = args.proof_root / suite / f'{rs_path.stem}-{case_key}'

    if case_root.exists():
        subprocess.run(['rm', '-rf', str(case_root)], check=True)
    case_root.mkdir(parents=True, exist_ok=True)

    flags = rustc_flags_for_file(rs_path)
    env = os.environ.copy()
    env['KMIR_EXTRA_RUSTC_FLAGS'] = ' '.join(flags)

    cmd = [
        'uv',
        '--project',
        'kmir',
        'run',
        '--python',
        'cpython-3.11.13',
        'kmir',
        'prove-rs',
        str(rs_path),
        '--max-depth',
        str(args.max_depth),
        '--proof-dir',
        str(case_root),
        '--reload',
    ]

    timeout_s = args.case_timeout if args.case_timeout > 0 else None
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
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

    duration_s = time.monotonic() - start
    status = _status_from_output(output or '')

    proof_id = f'{rs_path.stem}.main'
    linear_chain = _proof_linear_chain(case_root, proof_id)

    expected_status = SUITE_EXPECTED_STATUS[suite]
    require_linear = SUITE_REQUIRE_LINEAR_CHAIN[suite]

    if timed_out:
        return CaseResult(rel, 'failed', status, returncode, duration_s, linear_chain, 'timeout')

    if status is None:
        return CaseResult(rel, 'failed', status, returncode, duration_s, linear_chain, 'missing-status')

    if status != expected_status:
        return CaseResult(rel, 'failed', status, returncode, duration_s, linear_chain, f'status={status}')

    if require_linear and not linear_chain:
        return CaseResult(rel, 'failed', status, returncode, duration_s, linear_chain, 'non-linear-proof')

    return CaseResult(rel, 'passed', status, returncode, duration_s, linear_chain, 'ok')


def main() -> int:
    args = parse_args()
    if args.max_depth <= 0:
        raise ValueError('--max-depth must be > 0')
    if args.workers <= 0:
        raise ValueError('--workers must be > 0')
    if args.progress_every <= 0:
        raise ValueError('--progress-every must be > 0')

    discovered = discover_suite_rs_files(args.suite)
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

    started = time.monotonic()
    results: dict[str, str] = {}
    completed = 0
    total = len(discovered)
    sample_failures: list[dict[str, str | int | float | None]] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_case, args.suite, rel, args): rel for rel in discovered}
        for fut in as_completed(futures):
            completed += 1
            case = fut.result()
            results[case.rel] = case.outcome

            if case.outcome != 'passed' and len(sample_failures) < 40:
                sample_failures.append(
                    {
                        'path': case.rel,
                        'reason': case.reason,
                        'status': case.status,
                        'returncode': case.returncode,
                        'duration_seconds': round(case.duration_s, 3),
                        'linear_chain': case.linear_chain,
                    }
                )

            if completed % args.progress_every == 0 or case.outcome != 'passed':
                print(
                    f'[{completed}/{total}] {case.rel}: {case.outcome} '
                    f'(status={case.status}, linear={case.linear_chain}, reason={case.reason}, {case.duration_s:.1f}s)'
                )

    counts = {'passed': 0, 'failed': 0, 'skipped': 0, 'error': 0, 'xfailed': 0, 'notrun': 0}
    for outcome in results.values():
        counts[outcome] += 1

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
        'sample_failures': sample_failures,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + '\n')

    print(
        f"{args.suite}: total={total} passed={counts['passed']} failed={counts['failed']} elapsed={elapsed_s:.1f}s"
    )
    print(f'Wrote result file: {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
