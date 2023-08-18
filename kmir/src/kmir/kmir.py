__all__ = ['KMIR']

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from tempfile import NamedTemporaryFile
from typing import Optional, Union, final

from dotenv import load_dotenv
from pyk.cli.utils import check_dir_path, check_file_path
from pyk.kast.inner import KInner
from pyk.ktool.kprint import KAstInput, KAstOutput, _kast, gen_glr_parser
from pyk.ktool.krun import KRunOutput, _krun
from pyk.utils import BugReport

from .preprocessor import preprocess


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    haskell_dir: Path
    mir_parser: Path
    bug_report: BugReport | None

    def __init__(
        self,
        llvm_dir: Union[str, Path] | None,
        haskell_dir: Union[str, Path] | None,
        bug_report: BugReport | None = None,
    ):
        if llvm_dir is None or haskell_dir is None:
            load_dotenv()
        if llvm_dir is None:
            env_llvm_dir = os.getenv('KMIR_LLVM_DIR')
            if env_llvm_dir:
                llvm_dir = Path(env_llvm_dir)
            else:
                raise RuntimeError(
                    'Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR'
                )
        else:
            llvm_dir = Path(llvm_dir)
        check_dir_path(llvm_dir)

        mir_parser = llvm_dir / 'parser_Mir_MIR-PARSER-SYNTAX'
        if not mir_parser.is_file():
            mir_parser = gen_glr_parser(mir_parser, definition_dir=llvm_dir, module='MIR-PARSER-SYNTAX', sort='Mir')

        if haskell_dir is None:
            env_haskell_dir = os.getenv('KMIR_HASKELL_DIR')
            if env_haskell_dir:
                haskell_dir = Path(env_haskell_dir)
            else:
                # Haskell dir doesn't exist, but it not needed for current functionality
                print('WARN: Haskell defintion could not be found')
                haskell_dir = llvm_dir  # Just to pass type checking for now
        else:
            haskell_dir = Path(haskell_dir)
        check_dir_path(haskell_dir)

        object.__setattr__(self, 'llvm_dir', llvm_dir)
        object.__setattr__(self, 'haskell_dir', haskell_dir)
        object.__setattr__(self, 'mir_parser', mir_parser)
        object.__setattr__(self, 'bug_report', bug_report)

    def parse_program_raw(
        self,
        program_file: Union[str, Path],
        *,
        input: KAstInput,
        output: KAstOutput,
        temp_file: Optional[Union[str, Path]] = None,
    ) -> CompletedProcess:
        def parse(program_file: Path) -> CompletedProcess:
            try:
                if output == KAstOutput.KORE:
                    command = [str(self.mir_parser)] + [str(program_file)]
                    proc_res = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)
                else:
                    proc_res = _kast(
                        definition_dir=self.llvm_dir,
                        file=program_file,
                        input=input,
                        output=output,
                        sort='Mir',
                    )
            except CalledProcessError as err:
                raise ValueError("Couldn't parse program") from err
            return proc_res

        def preprocess_and_parse(program_file: Path, temp_file: Path) -> CompletedProcess:
            temp_file.write_text(preprocess(program_file.read_text()))
            return parse(temp_file)

        program_file = Path(program_file)
        check_file_path(program_file)

        if temp_file is None:
            with NamedTemporaryFile(mode='w') as f:
                temp_file = Path(f.name)
                return preprocess_and_parse(program_file, temp_file)

        temp_file = Path(temp_file)
        return preprocess_and_parse(program_file, temp_file)

    def parse_program(
        self,
        program_file: Union[str, Path],
        *,
        temp_file: Optional[Union[str, Path]] = None,
    ) -> KInner:
        proc_res = self.parse_program_raw(
            program_file=program_file,
            input=KAstInput.PROGRAM,
            output=KAstOutput.JSON,
            temp_file=temp_file,
        )

        return KInner.from_dict(json.loads(proc_res.stdout)['term'])

    def run_program(
        self,
        program_file: Union[str, Path],
        *,
        depth: int | None = None,
        output: KRunOutput = KRunOutput.NONE,
        check: bool = True,
        temp_file: Optional[Union[str, Path]] = None,
    ) -> CompletedProcess:
        def run(program_file: Path) -> CompletedProcess:
            return _krun(
                input_file=program_file,
                definition_dir=self.llvm_dir,
                output=output,
                check=check if depth is None else False,
                pipe_stderr=True,
                pmap={'PGM': str(self.mir_parser)},
                bug_report=self.bug_report,
                depth=depth,
            )

        def preprocess_and_run(program_file: Path, temp_file: Path) -> CompletedProcess:
            temp_file.write_text(preprocess(program_file.read_text()))
            return run(temp_file)

        program_file = Path(program_file)
        check_file_path(program_file)

        if temp_file is None:
            with NamedTemporaryFile(mode='w') as f:
                temp_file = Path(f.name)
                return preprocess_and_run(program_file, temp_file)

        temp_file = Path(temp_file)
        return preprocess_and_run(program_file, temp_file)
