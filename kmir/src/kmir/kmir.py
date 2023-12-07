__all__ = ['KMIR']

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Final, Optional, final

from pyk.kore.syntax import Pattern
from pyk.ktool.kprint import KPrint, gen_glr_parser
from pyk.ktool.kprove import KProve
from pyk.utils import BugReport, run_process

_LOGGER: Final = logging.getLogger(__name__)


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    mir_parser: Path
    llvm_interpreter: Path
    kprint: KPrint
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

        kprint = KPrint(llvm_dir)
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
        object.__setattr__(self, 'haskell_dir', haskell_dir)
        object.__setattr__(self, 'llvm_interpreter', llvm_interpreter)
        object.__setattr__(self, 'kprint', kprint)
        object.__setattr__(self, 'mir_symbolic', None)
        object.__setattr__(self, 'booster_interpreter', booster_interpreter)
        object.__setattr__(self, 'mir_prove', mir_prove)
        object.__setattr__(self, 'bug_report', bug_report)

    def mir_to_k(
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
        pgm: Pattern,
        depth: int | None = None,
    ) -> CompletedProcess:
        args = [str(self.llvm_interpreter), '/dev/stdin', str(depth), '/dev/stdout']
        try:
            res = run_process(args, input=pgm.text, pipe_stderr=True)
        except CalledProcessError as err:
            raise RuntimeError(f'kmir interpreter failed with status {err.returncode}: {err.stderr}') from err

        return res
