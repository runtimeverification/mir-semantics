from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun

if TYPE_CHECKING:
    from pathlib import Path


class KMIR(KProve, KRun):
    def __init__(self, definition_dir: Path) -> None:
        KProve.__init__(self, definition_dir)
        KRun.__init__(self, definition_dir)
