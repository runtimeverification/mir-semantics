__all__ = ['KMIR']

import logging
import subprocess
from subprocess import CompletedProcess, CalledProcessError
from dataclasses import dataclass
from pathlib import Path
from typing import Final, final, Optional

from pyk.ktool.kprint import gen_glr_parser
from pyk.ktool.kprove import KProve
from pyk.utils import BugReport, run_process

_LOGGER: Final = logging.getLogger(__name__)


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    haskell_dir: Path | None
    mir_parser: Path
    llvm_interpretor: Path
    mir_symbolic: Path | None
    booster_interpretor: Path | None
    bug_report: BugReport | None
    kprove: KProve | None

    def __init__(
        self,
        llvm_dir: Path,
        *,
        haskell_dir: Optional[Path] = None,
        #use_directory: Optional[Path] = None,
        bug_report: Optional[BugReport] = None, #TODO: shall we make the bug report by default?
    ):
        # the parser executor for mir syntax
        mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX' if llvm_dir else None
        mir_parser = gen_glr_parser(mir_parser, definition_dir=llvm_dir, module='MIR-SYNTAX', sort='Mir') if not mir_parser.is_file() else mir_parser

        #the run executor for interpreting mir programs
        llvm_interpretor = llvm_dir / 'interpretor'

        if haskell_dir:
            mir_prove = KProve(haskell_dir)
        #    mir_symbolic = 
            booster_interpretor = haskell_dir / 'llvmc' / 'interpretor.so'

        self.llvm_dir = llvm_dir
        self.mir_parser = mir_parser
        self.haskell_dir = haskell_dir
        self.llvm_interpretor = llvm_interpretor
        self.booster_interpretor = booster_interpretor
        self.mir_prove = mir_prove
        self.bug_report = bug_report

    def mir_to_k(
        self,
        program_file: Path,
        output: str,
    ) -> CompletedProcess:
        try:
            args = ['kast', str(self.mir_parser), str(program_file)] + ['--output ' + output]
            proc_res = run_process(args, stdout=subprocess.PIPE, check=True, text=True)
        except CalledProcessError as err:
            raise ValueError("Couldn't parse program") from err
        return proc_res
    
"""     def run_mir(
        self,
        program_file: Path
    ) -> CompletedProcess:
        kore_output = self.mir_to_k(program_file).stdout

        command = ['krun' +] """
