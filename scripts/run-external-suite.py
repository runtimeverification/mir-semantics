#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DATA_DIR = REPO_ROOT / 'kmir/src/tests/integration/data'

SUITE_TO_TEST_FILE = {
    'miri-pass': 'kmir/src/tests/integration/test_miri_pass.py',
    'miri-fail': 'kmir/src/tests/integration/test_miri_fail.py',
    'ui-run-pass': 'kmir/src/tests/integration/test_ui_run_pass.py',
    'kani': 'kmir/src/tests/integration/test_kani.py',
    'rustlantis': 'kmir/src/tests/integration/test_rustlantis.py',
}

NODE_ID_PARAM_PATTERN = re.compile(r'\[(.+)\]$')

OUTCOME_RANK = {
    'notrun': 0,
    'passed': 1,
    'xfailed': 2,
    'skipped': 3,
    'failed': 4,
    'error': 4,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run external suite tests with matrix skip bypassed and emit per-file results.'
    )
    parser.add_argument('--suite', choices=sorted(SUITE_TO_TEST_FILE), required=True, help='External suite to run.')
    parser.add_argument('--out', type=Path, required=True, help='Output JSON path.')
    parser.add_argument('--max-depth', type=int, default=200, help='max_depth passed to external harness.')
    parser.add_argument(
        '--numprocesses',
        type=int,
        default=0,
        help='Use xdist when > 0 (adds --numprocesses and --dist=worksteal).',
    )
    parser.add_argument(
        '--case-timeout',
        type=int,
        default=0,
        help='Per-test timeout in seconds (requires pytest-timeout).',
    )
    return parser.parse_args()


def discover_suite_rs_files(suite: str) -> list[str]:
    suite_dir = INTEGRATION_DATA_DIR / suite
    if not suite_dir.exists():
        return []
    return sorted(path.relative_to(INTEGRATION_DATA_DIR).as_posix() for path in suite_dir.rglob('*.rs') if path.is_file())


def nodeid_to_rel(nodeid: str) -> str | None:
    match = NODE_ID_PARAM_PATTERN.search(nodeid)
    if not match:
        return None
    return match.group(1)


@dataclass(eq=False)
class OutcomeCollector:
    outcome_by_rel: dict[str, str] = field(default_factory=dict)

    def _record_outcome(self, rel: str, outcome: str) -> None:
        current = self.outcome_by_rel.get(rel, 'notrun')
        if OUTCOME_RANK.get(outcome, 0) >= OUTCOME_RANK.get(current, 0):
            self.outcome_by_rel[rel] = outcome

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:  # pragma: no cover - pytest callback
        rel = nodeid_to_rel(report.nodeid)
        if rel is None:
            return
        if report.when not in ('setup', 'call'):
            return

        if report.when == 'setup' and report.outcome == 'failed':
            self._record_outcome(rel, 'error')
            return

        self._record_outcome(rel, report.outcome)


def main() -> int:
    args = parse_args()
    if args.max_depth <= 0:
        raise ValueError('--max-depth must be > 0')

    discovered = discover_suite_rs_files(args.suite)
    if not discovered:
        print(f'No .rs files discovered for suite {args.suite}', file=sys.stderr)
        return 1

    os.environ['KMIR_RUN_ALL_EXTERNAL'] = '1'
    os.environ['KMIR_EXTERNAL_MAX_DEPTH'] = str(args.max_depth)

    collector = OutcomeCollector()
    pytest_args = [str(REPO_ROOT / SUITE_TO_TEST_FILE[args.suite]), '-q', '--maxfail=0']
    if args.numprocesses > 0:
        pytest_args.extend(['--numprocesses', str(args.numprocesses), '--dist', 'worksteal'])
    if args.case_timeout > 0:
        pytest_args.extend(['--timeout', str(args.case_timeout), '--timeout-method', 'signal'])

    exit_code = int(pytest.main(pytest_args, plugins=[collector]))
    if exit_code not in (0, 1):
        print(f'pytest ended with infrastructure error exit code {exit_code}', file=sys.stderr)
        return exit_code

    outcome_by_rel = {rel: collector.outcome_by_rel.get(rel, 'notrun') for rel in discovered}
    counts = {'passed': 0, 'failed': 0, 'skipped': 0, 'error': 0, 'xfailed': 0, 'notrun': 0}
    for outcome in outcome_by_rel.values():
        counts[outcome] = counts.get(outcome, 0) + 1

    payload = {
        'suite': args.suite,
        'max_depth': args.max_depth,
        'numprocesses': args.numprocesses,
        'case_timeout': args.case_timeout,
        'pytest_exit_code': exit_code,
        'counts': counts,
        'results': outcome_by_rel,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + '\n')

    print(
        f"{args.suite}: total={len(discovered)} "
        f"passed={counts.get('passed', 0)} failed={counts.get('failed', 0)} "
        f"error={counts.get('error', 0)} skipped={counts.get('skipped', 0)} notrun={counts.get('notrun', 0)}"
    )
    print(f'Wrote result file: {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
