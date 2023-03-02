__all__ = ['KMIR']

import json
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from tempfile import NamedTemporaryFile
from typing import Optional, Union, final

from pyk.cli_utils import check_dir_path, check_file_path
from pyk.kast.inner import KInner
from pyk.ktool.kprint import KAstInput, KAstOutput, _kast
from pyk.ktool.krun import KRunOutput, _krun

from .preprocessor import preprocess


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
        check: bool = True,
        temp_file: Optional[Union[str, Path]] = None,
    ) -> CompletedProcess:
        def run(program_file: Path) -> CompletedProcess:
            return _krun(
                input_file=program_file,
                definition_dir=self.llvm_dir,
                output=KRunOutput.NONE,
                check=check,
                pipe_stderr=True,
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
