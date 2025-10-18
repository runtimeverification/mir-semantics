#!/usr/bin/env python3
"""Compare matching ``test_*`` functions across entrypoint files."""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

DEFAULT_PAIRS: List[Tuple[str, str]] = [
    ("p-token/src/entrypoint-runtime-verification.rs", "program/src/entrypoint-rvo.rs"),
    ("p-token/src/entrypoint-runtime-verification.rs", "program/src/entrypoint-runtime-verification.rs"),
]

TEST_FN_PATTERN = re.compile(r"(?m)^[ \t]*(?:pub[ \t]+)?fn[ \t]+(?P<name>test_[A-Za-z0-9_]+)")


def resolve_path(root: Path, candidate: str) -> Path:
    path = Path(candidate)
    if not path.is_absolute():
        path = (root / path).resolve()
    return path


def format_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_pair_specs(items: Iterable[str]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for spec in items:
        if ":" not in spec:
            raise ValueError(f"Invalid pair '{spec}', expected format left:right.")
        left, right = spec.split(":", 1)
        left, right = left.strip(), right.strip()
        if not left or not right:
            raise ValueError(f"Invalid pair '{spec}', both sides required.")
        pairs.append((left, right))
    return pairs


def extract_tests(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    tests: Dict[str, str] = {}
    for match in TEST_FN_PATTERN.finditer(text):
        start = match.start()
        brace_start = text.find("{", match.end())
        if brace_start == -1:
            print(f"Warning: no body found for {match.group('name')} in {path}", file=sys.stderr)
            continue
        try:
            brace_end = find_matching_brace(text, brace_start)
        except ValueError as exc:
            print(f"Warning: {exc} in {path}", file=sys.stderr)
            continue
        snippet = text[start : brace_end + 1].strip()
        tests[match.group("name")] = snippet
    return tests


def find_matching_brace(text: str, start: int) -> int:
    depth = 0
    i = start
    length = len(text)
    while i < length:
        ch = text[i]
        if text.startswith("//", i):
            newline = text.find("\n", i)
            if newline == -1:
                return length - 1
            i = newline + 1
            continue
        if text.startswith("/*", i):
            close = text.find("*/", i + 2)
            if close == -1:
                raise ValueError("Unterminated block comment")
            i = close + 2
            continue
        if ch == '"':
            i += 1
            while i < length:
                if text[i] == "\\":
                    i += 2
                elif text[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            continue
        if ch == "'":
            i += 1
            while i < length:
                if text[i] == "\\":
                    i += 2
                elif text[i] == "'":
                    i += 1
                    break
                else:
                    i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"Unmatched braces starting at index {start}")


def compare_pair(root: Path, left_rel: str, right_rel: str) -> None:
    left_path = resolve_path(root, left_rel)
    right_path = resolve_path(root, right_rel)
    left_label = format_relative(left_path, root)
    right_label = format_relative(right_path, root)

    if not left_path.is_file():
        print(f"Missing file: {left_label}", file=sys.stderr)
        return
    if not right_path.is_file():
        print(f"Missing file: {right_label}", file=sys.stderr)
        return

    left_tests = extract_tests(left_path)
    right_tests = extract_tests(right_path)

    left_names = set(left_tests)
    right_names = set(right_tests)

    common = sorted(left_names & right_names)
    only_left = sorted(left_names - right_names)
    only_right = sorted(right_names - left_names)

    identical: List[str] = []
    differing: List[str] = []
    for name in common:
        if left_tests[name] == right_tests[name]:
            identical.append(name)
        else:
            differing.append(name)

    print(f"== {left_label} vs {right_label} ==")
    if only_left:
        print(f"- Only in {left_label}: {', '.join(only_left)}")
    else:
        print(f"- Only in {left_label}: none")
    if only_right:
        print(f"- Only in {right_label}: {', '.join(only_right)}")
    else:
        print(f"- Only in {right_label}: none")
    if identical:
        print(f"- Identical tests: {', '.join(identical)}")
    else:
        print("- Identical tests: none")
    if differing:
        print("- Differences:")
        for name in differing:
            print(f"  * {name}")
            diff_lines = list(
                difflib.unified_diff(
                    left_tests[name].splitlines(),
                    right_tests[name].splitlines(),
                    fromfile=f"{left_label}:{name}",
                    tofile=f"{right_label}:{name}",
                    lineterm="",
                )
            )
            if not diff_lines:
                print("    (no textual diff generated)")
            else:
                for line in diff_lines:
                    print(f"    {line}")
    else:
        print("- Differences: none")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare matching test_* function definitions across entrypoint files."
    )
    parser.add_argument(
        "--pairs",
        metavar="LEFT:RIGHT",
        nargs="*",
        help="Optional list of file pairs to compare (relative to the repository root).",
    )
    parser.add_argument(
        "--rvo",
        action="store_true",
        help="Only compare against program/src/entrypoint-rvo.rs (default includes both pairs).",
    )
    parser.add_argument(
        "--rv",
        action="store_true",
        help="Only compare against program/src/entrypoint-runtime-verification.rs (default includes both pairs).",
    )
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    parents = script_path.parents
    repo_root = parents[3] if len(parents) >= 4 else script_path.parent

    if args.pairs and (args.rvo or args.rv):
        parser.error("--pairs cannot be combined with --rvo/--rv filters.")

    if args.pairs:
        try:
            pairs = parse_pair_specs(args.pairs)
        except ValueError as exc:
            parser.error(str(exc))
    else:
        selected_pairs: List[Tuple[str, str]] = []
        if args.rvo:
            selected_pairs.append(DEFAULT_PAIRS[0])
        if args.rv:
            selected_pairs.append(DEFAULT_PAIRS[1])
        pairs = selected_pairs or DEFAULT_PAIRS

    for index, (left_rel, right_rel) in enumerate(pairs):
        if index:
            print()
        compare_pair(repo_root, left_rel, right_rel)


if __name__ == "__main__":
    main()
