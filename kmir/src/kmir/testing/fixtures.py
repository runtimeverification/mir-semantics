from __future__ import annotations

import re
import sys
from difflib import unified_diff
from typing import TYPE_CHECKING

import pytest

from kmir.build import HASKELL_DEF_DIR, LLVM_LIB_DIR
from kmir.kmir import KMIR

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import FixtureRequest, Parser


def pytest_configure(config) -> None:
    sys.setrecursionlimit(1000000)


def _normalize_symbol_hashes(text: str) -> str:
    """Normalize rustc symbol hash suffixes that drift across builds/environments."""
    # Normalize mangled symbol hashes, including generic names with `$` and `.`.
    # Keep trailing `E` when present; truncated variants may omit it.
    text = re.sub(r'(_ZN[0-9A-Za-z_$.]+17h)[0-9a-fA-F]+E', r'\1<hash>E', text)
    text = re.sub(r'(_ZN[0-9A-Za-z_$.]+17h)[0-9a-fA-F]+', r'\1<hash>', text)
    # Normalize demangled hash suffixes (`...::h<hex>`).
    text = re.sub(r'(::h)[0-9a-fA-F]{8,}', r'\1<hash>', text)
    return text


def assert_or_update_show_output(
    actual_text: str, expected_file: Path, *, update: bool, path_replacements: dict[str, str] | None = None
) -> None:
    if path_replacements:
        for old, new in path_replacements.items():
            actual_text = actual_text.replace(old, new)
    # Normalize rustc symbol hash suffixes that can drift across builds/environments.
    actual_text = _normalize_symbol_hashes(actual_text)
    if update:
        expected_file.write_text(actual_text)
    else:
        assert expected_file.is_file()
        expected_text = expected_file.read_text()
        expected_text = _normalize_symbol_hashes(expected_text)
        if actual_text != expected_text:
            diff = '\n'.join(
                unified_diff(
                    expected_text.splitlines(),
                    actual_text.splitlines(),
                    fromfile=str(expected_file),
                    tofile='actual_text',
                    lineterm='',
                )
            )
            raise AssertionError(f'The actual output does not match the expected output:\n{diff}')


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        '--update-expected-output',
        action='store_true',
        default=False,
        help='Write expected output files for proof tests',
    )


@pytest.fixture
def update_expected_output(request: FixtureRequest) -> bool:
    return request.config.getoption('--update-expected-output')


@pytest.fixture
def kmir() -> KMIR:
    return KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
