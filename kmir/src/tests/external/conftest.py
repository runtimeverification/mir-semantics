from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest import FixtureRequest, Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        '--update-skip',
        action='store_true',
        default=False,
        help='Shrink stable-mir-ui skip entries by rerunning only current skip.txt cases.',
    )


@pytest.fixture(scope='session')
def update_skip_mode(request: FixtureRequest) -> bool:
    return request.config.getoption('--update-skip')
