from pyk.kdist import kdist

from .tools import Tools


def llvm_semantics() -> Tools:
    return Tools(definition_dir=kdist.get('mir-semantics.llvm'))


def haskell_semantics() -> Tools:
    return Tools(definition_dir=kdist.get('mir-semantics.haskell'))
