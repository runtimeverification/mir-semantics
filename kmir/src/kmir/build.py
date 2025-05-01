from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kdist import kdist

if TYPE_CHECKING:
    from typing import Final

LLVM_DEF_DIR: Final = kdist.which('mir-semantics.llvm')
LLVM_LIB_DIR: Final = kdist.which('mir-semantics.llvm-library')
HASKELL_DEF_DIR: Final = kdist.which('mir-semantics.haskell')
