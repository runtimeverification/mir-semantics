__all__ = ['KMIR']

import json
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
from typing import Optional, Union, final

from pyk.cli_utils import check_dir_path, check_file_path
from pyk.kast.inner import KInner
from pyk.ktool.kprint import KAstInput, KAstOutput, _kast

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

    def parse_program(
        self,
        program_file: Union[str, Path],
        *,
        temp_file: Optional[Union[str, Path]] = None,
    ) -> KInner:
        def parse(program_file: Path) -> KInner:
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

        def preprocess_and_parse(program_file: Path, temp_file: Path) -> KInner:
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
