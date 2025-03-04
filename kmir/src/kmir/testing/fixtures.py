from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kmir.build import HASKELL_DEF_DIR, LLVM_LIB_DIR, llvm_semantics
from kmir.kmir import KMIR

if TYPE_CHECKING:
    from kmir.tools import Tools


@pytest.fixture
def tools() -> Tools:
    return llvm_semantics()


@pytest.fixture
def kmir() -> KMIR:
    return KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
