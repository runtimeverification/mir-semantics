from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyk.kast import KInner
    from pyk.ktool.kprint import KPrint


def kast_print(kast: KInner, *, kprint: KPrint) -> str:
    # TODO: copied from riscv-semantics, which should be upstreamed to pyk
    from pyk.konvert import kast_to_kore
    from pyk.kore.tools import kore_print

    kore = kast_to_kore(kprint.definition, kast)
    return kore_print(kore, definition_dir=kprint.definition_dir)
