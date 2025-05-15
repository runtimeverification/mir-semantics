from __future__ import annotations

from difflib import unified_diff
from typing import TYPE_CHECKING

import pytest

from kmir.build import HASKELL_DEF_DIR, LLVM_LIB_DIR
from kmir.kmir import KMIR

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import FixtureRequest, Parser


def assert_or_update_show_output(actual_text: str, expected_file: Path, *, update: bool) -> None:
    if update:
        expected_file.write_text(actual_text)
    else:
        assert expected_file.is_file()
        expected_text = expected_file.read_text()
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
