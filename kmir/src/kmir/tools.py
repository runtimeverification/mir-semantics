from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.ktool.krun import KRun
from pyk.kast.outer import read_kast_definition

from .kparse import KParse

if TYPE_CHECKING:
    from pathlib import Path

    from pyk.kast.outer import KDefinition
    from pyk.ktool.kprint import KPrint


class Tools:
    __kparse: KParse
    __krun: KRun
    __definition: KDefinition

    def __init__(
        self,
        definition_dir: Path,
    ) -> None:
        self.__kparse = KParse(definition_dir)
        self.__krun = KRun(definition_dir)
        self.__definition = read_kast_definition(definition_dir / 'compiled.json')

    @property
    def kparse(self) -> KParse:
        return self.__kparse

    @property
    def kprint(self) -> KPrint:
        return self.__krun

    @property
    def krun(self) -> KRun:
        return self.__krun

    @property
    def definition(self) -> KDefinition:
        return self.__definition
