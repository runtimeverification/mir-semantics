from __future__ import annotations

from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Callable, Iterable

from pyk.kore.parser import KoreParser
from pyk.ktool.kprint import KPrint
from pyk.utils import run_process

if TYPE_CHECKING:
    from pathlib import Path
    from subprocess import CompletedProcess

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
        result = _kparse(input_file=input_file, definition_dir=self.definition_dir, sort=sort)
        kore = KoreParser(result.stdout).pattern()
        kast = self.kore_to_kast(kore)
        return (result.returncode, kast)


def _kparse(
    command: str = 'kparse',
    *,
    input_file: Path | None = None,
    definition_dir: Path | None = None,
    sort: str | None = None,
) -> CompletedProcess:
    args = _build_arg_list(
        command=command,
        input_file=input_file,
        definition_dir=definition_dir,
        sort=sort,
    )

    try:
        return run_process(args=args)
    except CalledProcessError as err:
        raise RuntimeError(
            f'Command kparse exited with code {err.returncode} for: {input_file}', err.stdout, err.stderr
        ) from err


def _build_arg_list(
    *,
    command: str,
    input_file: Path | None,
    definition_dir: Path | None,
    sort: str | None,
) -> list[str]:
    args = [command]

    if input_file:
        args += [str(input_file)]

    if definition_dir:
        args += ['--definition', str(definition_dir)]

    if sort:
        args += ['--sort', sort]

    return args
