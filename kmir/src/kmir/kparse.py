from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.ktool.kprint import KPrint

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path

    from pyk.kast.inner import KInner
    from pyk.kast.outer import KFlatModule
    from pyk.kast.pretty import SymbolTable
    from pyk.utils import BugReport


class KParse(KPrint):
    parser: str

    def __init__(
        self,
        definition_dir: Path,
        use_directory: Path | None = None,
        bug_report: BugReport | None = None,
        extra_unparsing_modules: Iterable[KFlatModule] = (),
        patch_symbol_table: Callable[[SymbolTable], None] | None = None,
        command: str = 'kparse',
    ):
        super().__init__(
            definition_dir,
            use_directory=use_directory,
            bug_report=bug_report,
            extra_unparsing_modules=extra_unparsing_modules,
            patch_symbol_table=patch_symbol_table,
        )
        self.parser = command

    def kparse(self, input_file: Path, *, sort: str) -> tuple[int, KInner]:
        from pyk.kore.parser import KoreParser
        from pyk.ktool.kprint import _kast

        result = _kast(
            file=input_file,
            definition_dir=self.definition_dir,
            sort=sort,
            input='rule',
            output='kore',
        )
        kore = KoreParser(result.stdout).pattern()
        kast = self.kore_to_kast(kore)
        return (result.returncode, kast)
