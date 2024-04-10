import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Final

from pyk.cli.args import LoggingOptions

from .kmir import KMIR
from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


class RunOptions(LoggingOptions):
    mir_file: Path
    definition_dir: Path | None
    output: str
    bug_report: bool
    depth: int | None

    @staticmethod
    def default() -> dict[str, Any]:
        llvm_dir_str = os.getenv('KMIR_LLVM_DIR')
        llvm_dir = Path(llvm_dir_str) if llvm_dir_str is not None else None

        return {
            'definition_dir': llvm_dir,
            'output': 'pretty',
            'bug_report': False,
            'depth': None,
        }


def run(
    kmir: KMIR,
    options: RunOptions,
    # bug_report
    temp_file: Path | None = None,
) -> None:
    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = Path(temp_file)

    preprocess_mir_file(options.mir_file, temp_file)

    proc_res = kmir.mir_to_kore(options.mir_file)

    # TODO: what should we do to the bug_report, reference pyk.ktools.krun._krun()
    """     if kmir.bug_report is not None:
        new_input_file = Path(f'krun_inputs/{options.mir_file}')
        bug_report.add_file(options.mir_file, new_input_file)
        bug_report.add_command([a if a != str(options.mir_file) else str(new_input_file) for a in args]) """

    proc_res = kmir.interpret_mir_to_kore(proc_res.stdout, options.depth)

    kmir.print_kore_to_xxx(proc_res.stdout, options.output)
