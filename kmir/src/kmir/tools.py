from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kast.inner import KSort, Subst
from pyk.kast.outer import read_kast_definition
from pyk.ktool.krun import KRun
from pyk.prelude.string import stringToken

from .kparse import KParse

if TYPE_CHECKING:
    from pathlib import Path

    from pyk.kast import KInner
    from pyk.kast.outer import KDefinition
    from pyk.kore.syntax import Pattern
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

    def run_parsed(self, parsed_smir: KInner, start_symbol: KInner | str = 'main', depth: int | None = None) -> Pattern:
        init_config = self.make_init_config(parsed_smir, start_symbol)
        init_kore = self.krun.kast_to_kore(init_config, KSort('GeneratedTopCell'))
        result = self.krun.run_pattern(init_kore, depth=depth)

        return result

    def make_init_config(
        self, parsed_smir: KInner, start_symbol: KInner | str = 'main', sort: str = 'GeneratedTopCell'
    ) -> KInner:
        if isinstance(start_symbol, str):
            start_symbol = stringToken(start_symbol)

        subst = Subst({'$PGM': parsed_smir, '$STARTSYM': start_symbol})
        init_config = subst.apply(self.definition.init_config(KSort(sort)))
        return init_config
