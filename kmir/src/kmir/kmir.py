__all__ = ['KMIR']

import logging
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Final, Optional, final

from pyk.kore.parser import KoreParser
from pyk.kore.prelude import SORT_K_ITEM, inj, top_cell_initializer
from pyk.kore.syntax import Pattern, SortApp
from pyk.kore.tools import PrintOutput, kore_print

from pyk.ktool.kprint import gen_glr_parser
from pyk.ktool.kprove import KProve
from pyk.utils import BugReport, run_process

_LOGGER: Final = logging.getLogger(__name__)


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    mir_parser: Path
    llvm_interpreter: Path
    haskell_dir: Path | None
    mir_symbolic: Path | None
    booster_interpreter: Path | None
    bug_report: BugReport | None
    kprove: KProve | None

    def __init__(
        self,
        llvm_dir: Path,
        *,
        haskell_dir: Optional[Path] = None,
        # use_directory: Optional[Path] = None,
        bug_report: Optional[BugReport] = None,  # TODO: shall we make the bug report by default?
    ):
        # the parser executor for mir syntax
        mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'
        if not mir_parser.is_file():
            mir_parser = gen_glr_parser(mir_parser, definition_dir=llvm_dir, module='MIR-SYNTAX', sort='Mir')
        else:
            mir_parser = mir_parser

        # the run executor for interpreting mir programs
        llvm_interpreter = llvm_dir / 'interpreter'

        if haskell_dir:
            mir_prove = KProve(haskell_dir)
            # mir_symbolic = None
            booster_interpreter = haskell_dir / 'llvmc' / 'interpreter.so'
        else:
            mir_prove = None
            # mir_symbolic = None
            booster_interpreter = None

        object.__setattr__(self, 'llvm_dir', llvm_dir)
        object.__setattr__(self, 'mir_parser', mir_parser)
        object.__setattr__(self, 'llvm_interpreter', llvm_interpreter)

        object.__setattr__(self, 'haskell_dir', haskell_dir)
        object.__setattr__(self, 'mir_symbolic', None)
        object.__setattr__(self, 'booster_interpreter', booster_interpreter)
        object.__setattr__(self, 'mir_prove', mir_prove)

        object.__setattr__(self, 'bug_report', bug_report)

    def mir_to_kore(
        self,
        mir_file: Path,
    ) -> CompletedProcess:
        args = [str(self.mir_parser), str(mir_file)]

        try:
            # proc_res.stdout would always be KORE
            # check is by default True, which raises runrime error if proc_res.returncode is nonzero
            # what is exec_process? Debugger?
            proc_res = run_process(args, logger=_LOGGER)
        except CalledProcessError as err:
            raise RuntimeError(f'kmir parser failed with status {err.returncode}: {err.stderr}') from err
        return proc_res

    def interpret_mir_to_kore(
        self,
        pgm: str | Pattern,
        depth: int | None = None,
    ) -> CompletedProcess:
        if not isinstance(pgm, Pattern):
            pgm = KoreParser(pgm).pattern()

        depth = depth if depth is not None else -1
        args = [str(self.llvm_interpreter), '/dev/stdin', str(depth), '/dev/stdout']

        init_config = top_cell_initializer({'$PGM': inj(SortApp('SortMir'), SORT_K_ITEM, pgm)})
        try:
            res = run_process(args, input=init_config.text, pipe_stderr=True)
        except CalledProcessError as err:
            raise RuntimeError(f'kmir interpreter failed with status {err.returncode}: {err.stderr}') from err

        return res

    def print_kore_to_xxx(self, kore_text: str | Pattern, output: str) -> None:
        output_format = PrintOutput(output)

        match output_format:
            case PrintOutput.NONE:
                None
            case PrintOutput.KORE:
                print(kore_text)
            case PrintOutput.JSON | PrintOutput.PRETTY | PrintOutput.PROGRAM | PrintOutput.KAST | PrintOutput.LATEX | PrintOutput.BINARY:
                kore_pattern = KoreParser(kore_text).pattern()
                print(kore_print(kore_pattern, self.llvm_dir, output_format))
                # replace kore_print with run_process, make use of the executable, turn the color on.
            case _:
                raise ValueError('Output format not supported.')
