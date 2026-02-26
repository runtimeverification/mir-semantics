#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX_PATH = REPO_ROOT / 'docs' / 'coverage-matrix.json'
INTEGRATION_DATA_DIR = REPO_ROOT / 'kmir/src/tests/integration/data'
BODY_MD_PATH = REPO_ROOT / 'kmir/src/kmir/kdist/mir-semantics/body.md'
TY_MD_PATH = REPO_ROOT / 'kmir/src/kmir/kdist/mir-semantics/ty.md'

LOCAL_SUITES = ('prove-rs', 'exec-smir', 'run-rs', 'ub')
EXTERNAL_SUITES = ('miri-pass', 'miri-fail', 'ui-run-pass', 'kani', 'rustlantis')

REQUIRED_SECTIONS = (
    'types/boolean',
    'types/numeric-integer',
    'types/numeric-float',
    'types/textual-char',
    'types/textual-str',
    'types/never',
    'types/tuple',
    'types/array',
    'types/slice',
    'types/struct',
    'types/enum',
    'types/union',
    'types/function-pointer',
    'types/closure',
    'types/pointer-reference',
    'types/pointer-raw',
    'types/function-item',
    'types/trait-object',
    'expressions/literals',
    'expressions/paths',
    'expressions/blocks',
    'expressions/operators-arithmetic',
    'expressions/operators-bitwise',
    'expressions/operators-comparison',
    'expressions/operators-logical',
    'expressions/operators-negation',
    'expressions/operators-dereference',
    'expressions/operators-borrow',
    'expressions/operators-assignment',
    'expressions/operators-compound-assignment',
    'expressions/grouped',
    'expressions/array',
    'expressions/tuple',
    'expressions/struct',
    'expressions/call',
    'expressions/method-call',
    'expressions/field-access',
    'expressions/closure',
    'expressions/loop',
    'expressions/range',
    'expressions/if-iflet',
    'expressions/match',
    'expressions/return',
    'expressions/await',
    'statements/let',
    'statements/expression',
    'statements/item',
    'patterns/literal',
    'patterns/identifier',
    'patterns/wildcard',
    'patterns/rest',
    'patterns/range',
    'patterns/reference',
    'patterns/struct',
    'patterns/tuple-struct',
    'patterns/tuple',
    'patterns/grouped',
    'patterns/slice',
    'patterns/path',
    'patterns/or',
    'type-system/layout',
    'type-system/interior-mutability',
    'type-system/coercions',
    'type-system/destructors-drop',
    'type-system/dynamically-sized-types',
    'memory-model/allocation',
    'memory-model/lifetime',
    'memory-model/variables',
    'unsafety/undefined-behavior',
    'panic/unwinding',
    'panic/abort',
    'constant-evaluation/const-contexts',
    'constant-evaluation/const-functions',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate and validate MIR semantics coverage matrix report.')
    parser.add_argument('--matrix', type=Path, default=DEFAULT_MATRIX_PATH, help='Path to coverage matrix JSON.')
    parser.add_argument('--summary', action='store_true', help='Print covered/partial/gap summary.')
    parser.add_argument('--suite-stats', action='store_true', help='Print per-suite statistics.')
    parser.add_argument('--top-gaps', type=int, default=10, help='Print top N gap/partial sections.')
    parser.add_argument('--validate', action='store_true', help='Run completeness validation; returns non-zero on errors.')
    return parser.parse_args()


def load_matrix(matrix_path: Path) -> dict:
    return json.loads(matrix_path.read_text())


def section_status(section_entry: dict) -> str:
    tests_count = sum(len(paths) for paths in section_entry.get('tests', {}).values())
    skip_count = sum(len(paths) for paths in section_entry.get('skip', {}).values())
    if tests_count == 0 and skip_count == 0:
        return 'gap'
    if skip_count > 0:
        return 'partial'
    return 'covered'


def discover_suite_files(suite: str) -> set[str]:
    base = INTEGRATION_DATA_DIR / suite
    if not base.exists():
        return set()

    if suite == 'prove-rs':
        files = {
            path.relative_to(INTEGRATION_DATA_DIR).as_posix()
            for path in base.rglob('*')
            if path.is_file() and path.suffix in {'.rs', '.json'} and '/show/' not in path.as_posix()
        }
        return files
    if suite == 'exec-smir':
        files = {
            path.relative_to(INTEGRATION_DATA_DIR).as_posix()
            for path in base.rglob('*')
            if path.is_file() and (path.suffix == '.rs' or path.name.endswith('.smir.json'))
        }
        return files
    if suite in ('run-rs', 'ub', 'miri-pass', 'miri-fail', 'ui-run-pass', 'kani', 'rustlantis'):
        return {
            path.relative_to(INTEGRATION_DATA_DIR).as_posix()
            for path in base.rglob('*.rs')
            if path.is_file()
        }
    return set()


def parse_expected_smir_elements() -> set[str]:
    patterns = (
        r'symbol\((Rvalue|TerminatorKind|CastKind|BinOp|UnOp|NullOp|TyKind|Operand|ProjectionElem)::([A-Za-z0-9_]+)\)'
    )
    expected: set[str] = set()
    for path in (BODY_MD_PATH, TY_MD_PATH):
        text = path.read_text()
        for kind, variant in re.findall(patterns, text):
            expected.add(f'{kind}::{variant}')
    return expected


def collect_declared_files(matrix: dict, suite: str, *, tests_only: bool) -> set[str]:
    sections: dict[str, dict] = matrix.get('sections', {})
    declared: set[str] = set()
    for entry in sections.values():
        declared.update(entry.get('tests', {}).get(suite, []))
        if not tests_only:
            declared.update(entry.get('skip', {}).get(suite, []))
    return declared


def validate_matrix(matrix: dict) -> list[str]:
    errors: list[str] = []
    sections: dict[str, dict] = matrix.get('sections', {})

    missing_sections = [section for section in REQUIRED_SECTIONS if section not in sections]
    if missing_sections:
        errors.append(f'Missing required sections: {", ".join(missing_sections)}')

    expected_elements = parse_expected_smir_elements()
    mapped_elements: set[str] = set()
    for entry in sections.values():
        mapped_elements.update(entry.get('smir_elements', []))
    missing_elements = sorted(expected_elements - mapped_elements)
    if missing_elements:
        errors.append(f'Unmapped Stable MIR elements: {", ".join(missing_elements)}')

    for suite in LOCAL_SUITES:
        discovered = discover_suite_files(suite)
        declared_tests = collect_declared_files(matrix, suite, tests_only=True)
        missing = sorted(discovered - declared_tests)
        if missing:
            errors.append(f'Local suite {suite} has unmapped tests (must be in tests): {", ".join(missing)}')

    for suite in EXTERNAL_SUITES:
        discovered = discover_suite_files(suite)
        if not discovered:
            continue
        declared = collect_declared_files(matrix, suite, tests_only=False)
        missing = sorted(discovered - declared)
        if missing:
            errors.append(f'External suite {suite} has unmapped files (must be in tests or skip): {", ".join(missing)}')

    for section_name, entry in sections.items():
        if section_status(entry) == 'gap' and not entry.get('note', '').strip():
            errors.append(f'Section {section_name} is a gap but has no documented rationale in "note".')

    return errors


def print_summary(matrix: dict) -> None:
    counts = defaultdict(int)
    for entry in matrix.get('sections', {}).values():
        counts[section_status(entry)] += 1

    total = sum(counts.values())
    print('Coverage summary:')
    print(f'  sections total: {total}')
    print(f'  covered: {counts["covered"]}')
    print(f'  partial: {counts["partial"]}')
    print(f'  gap: {counts["gap"]}')


def print_suite_stats(matrix: dict) -> None:
    sections: dict[str, dict] = matrix.get('sections', {})
    suites = matrix.get('suite_order') or [*LOCAL_SUITES, *EXTERNAL_SUITES]
    suite_policy: dict[str, str] = matrix.get('suite_policy', {})

    print('Per-suite stats:')
    for suite in suites:
        tests = set()
        skip = set()
        for entry in sections.values():
            tests.update(entry.get('tests', {}).get(suite, []))
            skip.update(entry.get('skip', {}).get(suite, []))
        total = len(tests) + len(skip)
        passing_rate = 0.0 if total == 0 else (len(tests) / total) * 100
        policy = suite_policy.get(suite)
        policy_suffix = f' policy={policy}' if policy else ''
        print(
            f'  {suite}: tests={len(tests)} skip={len(skip)} total={total} pass_like={passing_rate:.1f}%{policy_suffix}'
        )


def print_top_gaps(matrix: dict, top_n: int) -> None:
    ranked = []
    for section_name, entry in matrix.get('sections', {}).items():
        tests_count = sum(len(paths) for paths in entry.get('tests', {}).values())
        skip_count = sum(len(paths) for paths in entry.get('skip', {}).values())
        status = section_status(entry)
        gap_score = skip_count + (1 if status == 'gap' else 0)
        ranked.append((gap_score, skip_count, tests_count, section_name, status))

    ranked.sort(key=lambda item: (-item[0], -item[1], item[3]))
    print(f'Top {top_n} gap areas:')
    for _, skip_count, tests_count, section_name, status in ranked[:top_n]:
        print(f'  {section_name}: status={status} tests={tests_count} skip={skip_count}')


def main() -> int:
    args = parse_args()
    matrix = load_matrix(args.matrix)

    if not any((args.summary, args.suite_stats, args.validate)):
        args.summary = True
        args.suite_stats = True

    if args.summary:
        print_summary(matrix)
    if args.suite_stats:
        print_suite_stats(matrix)
    print_top_gaps(matrix, args.top_gaps)

    if args.validate:
        errors = validate_matrix(matrix)
        if errors:
            print('Validation failed:')
            for err in errors:
                print(f'  - {err}')
            return 1
        print('Validation passed.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
