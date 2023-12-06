# import logging

from pathlib import Path
from subprocess import CompletedProcess
from tempfile import NamedTemporaryFile
from typing import Optional

from pyk.ktool.krun import KRunOutput, _krun
from pyk.utils import BugReport

from .utils import preprocess_mir_file


def run(
    llvm_dir: Path,
    mir_file: Path,
    *,
    depth: int | None = None,
    output: str = 'none',
    check: bool = True,
    bug_report: BugReport | None = None,
    temp_file: Optional[Path] = None,
) -> CompletedProcess:
    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = Path(temp_file)

    preprocess_mir_file(mir_file, temp_file)

    mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'

    return _krun(
        input_file=mir_file,
        definition_dir=llvm_dir,
        output=KRunOutput[output.upper()],
        check=check if not depth else False,
        pipe_stderr=True,
        pmap={'PGM': str(mir_parser)},
        bug_report=bug_report,
        depth=depth,
        no_expand_macros=True,
    )
