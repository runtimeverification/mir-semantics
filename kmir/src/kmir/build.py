from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kdist import kdist

from .tools import Tools

if TYPE_CHECKING:
    from typing import Final

LLVM_DEF_DIR: Final = kdist.get('mir-semantics.llvm')
LLVM_LIB_DIR: Final = kdist.get('mir-semantics.llvm-library')
HASKELL_DEF_DIR: Final = kdist.get('mir-semantics.haskell')


def semantics() -> Tools:
    return Tools(definition_dir=LLVM_DEF_DIR)
