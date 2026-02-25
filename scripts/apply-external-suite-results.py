#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX_PATH = REPO_ROOT / 'docs/coverage-matrix.json'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Apply external-suite real-run results to coverage-matrix.json')
    parser.add_argument(
        '--matrix',
        type=Path,
        default=DEFAULT_MATRIX_PATH,
        help='Path to docs/coverage-matrix.json',
    )
    parser.add_argument(
        '--results',
        type=Path,
        nargs='+',
        required=True,
        help='One or more JSON files emitted by scripts/run-external-suite.py',
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def suite_declared_entries(sections: dict[str, dict], suite: str) -> set[str]:
    declared: set[str] = set()
    for entry in sections.values():
        declared.update(entry.get('tests', {}).get(suite, []))
        declared.update(entry.get('skip', {}).get(suite, []))
    return declared


def update_suite(sections: dict[str, dict], suite: str, statuses: dict[str, str]) -> dict[str, int]:
    passed = {rel for rel, outcome in statuses.items() if outcome == 'passed'}
    non_pass = set(statuses) - passed

    stats = {
        'passed': len(passed),
        'non_pass': len(non_pass),
        'moved_to_tests': 0,
        'moved_to_skip': 0,
        'removed_from_tests': 0,
        'removed_from_skip': 0,
    }

    for entry in sections.values():
        tests_bucket = entry.setdefault('tests', {})
        skip_bucket = entry.setdefault('skip', {})

        tests = set(tests_bucket.get(suite, []))
        skip = set(skip_bucket.get(suite, []))
        combined = tests | skip
        if not combined:
            continue

        newly_to_tests = (combined & passed) - tests
        newly_to_skip = (combined & non_pass) - skip
        stats['moved_to_tests'] += len(newly_to_tests)
        stats['moved_to_skip'] += len(newly_to_skip)
        stats['removed_from_tests'] += len(tests & non_pass)
        stats['removed_from_skip'] += len(skip & passed)

        new_tests = sorted((tests | (combined & passed)) - non_pass)
        new_skip = sorted((skip | (combined & non_pass)) - passed)

        if new_tests:
            tests_bucket[suite] = new_tests
        elif suite in tests_bucket:
            del tests_bucket[suite]

        if new_skip:
            skip_bucket[suite] = new_skip
        elif suite in skip_bucket:
            del skip_bucket[suite]

        if not tests_bucket:
            entry.pop('tests', None)
        if not skip_bucket:
            entry.pop('skip', None)

    return stats


def main() -> int:
    args = parse_args()
    matrix = load_json(args.matrix)
    sections: dict[str, dict] = matrix['sections']

    for result_path in args.results:
        payload = load_json(result_path)
        suite = payload['suite']
        statuses: dict[str, str] = payload['results']
        declared = suite_declared_entries(sections, suite)
        unknown = sorted(set(statuses) - declared)
        if unknown:
            raise ValueError(
                f'Result file {result_path} contains {len(unknown)} suite paths not declared in matrix for {suite}'
            )

        stats = update_suite(sections, suite, statuses)
        print(
            f'[{suite}] passed={stats["passed"]} non_pass={stats["non_pass"]} '
            f'moved_to_tests={stats["moved_to_tests"]} moved_to_skip={stats["moved_to_skip"]}'
        )

    args.matrix.write_text(json.dumps(matrix, indent=2) + '\n')
    print(f'Updated matrix: {args.matrix}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
