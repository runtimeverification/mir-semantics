from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kmir.build import semantics

if TYPE_CHECKING:
    from kmir.tools import Tools


@pytest.fixture
def tools() -> Tools:
    return semantics()
