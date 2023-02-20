__all__ = ['KMIR']

import json
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Union, final

from pyk.cli_utils import check_dir_path, check_file_path
from pyk.kast.inner import KInner
from pyk.ktool.kprint import KAstInput, KAstOutput, _kast
from pyk.ktool.krun import KRunOutput, _krun


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    haskell_dir: Path

    def __init__(self, llvm_dir: Union[str, Path], haskell_dir: Union[str, Path]):
        llvm_dir = Path(llvm_dir)
        check_dir_path(llvm_dir)

        haskell_dir = Path(haskell_dir)
        check_dir_path(haskell_dir)

        object.__setattr__(self, 'llvm_dir', llvm_dir)
        object.__setattr__(self, 'haskell_dir', haskell_dir)

    def parse_program(self, program_file: Union[str, Path]) -> KInner:
        program_file = Path(program_file)
        check_file_path(program_file)
        try:
            proc_res = _kast(
                definition_dir=self.llvm_dir,
                input_file=program_file,
                input=KAstInput.PROGRAM,
                output=KAstOutput.JSON,
                sort='Mir',
            )
        except CalledProcessError as err:
            raise ValueError("Couldn't parse program") from err

        return KInner.from_dict(json.loads(proc_res.stdout)['term'])

    def run_program(self, program_file: Union[str, Path], check: bool = True) -> CompletedProcess:
        program_file = Path(program_file)
        check_file_path(program_file)

        try:
            proc_res = _krun(
                input_file=program_file,
                definition_dir=self.llvm_dir,
                output=KRunOutput.NONE,
                check=check,
                pipe_stderr=True,
            )
        except CalledProcessError as err:
            raise err

        return proc_res
