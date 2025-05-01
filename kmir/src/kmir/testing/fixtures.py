from __future__ import annotations

import pytest

from kmir.build import HASKELL_DEF_DIR, LLVM_DEF_DIR, LLVM_LIB_DIR
from kmir.kmir import KMIR


@pytest.fixture
def kmir_haskell() -> KMIR:
    return KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)


@pytest.fixture
def kmir_llvm() -> KMIR:
    return KMIR(LLVM_DEF_DIR)
