from __future__ import annotations

from typing import TYPE_CHECKING

from .kparse import KParse

if TYPE_CHECKING:
    from pathlib import Path


class Tools:
    __kparse: KParse

    def __init__(
        self,
        definition_dir: Path,
    ) -> None:
        self.__kparse = KParse(definition_dir)

    @property
    def kparse(self) -> KParse:
        return self.__kparse
