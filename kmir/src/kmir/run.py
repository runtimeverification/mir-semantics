import logging

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final

from .kmir import KMIR
from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

def run(
    kmir: KMIR,
    mir_file: Path,
    *,
    depth: int | None = None,
    output: str = 'none',
    temp_file: Path | None = None,
) -> None:
    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = Path(temp_file)

    preprocess_mir_file(mir_file, temp_file)
 
    proc_res = kmir.mir_to_kore(mir_file)

    # TODO: what should we do to the bug_report, reference pyk.ktools.krun._krun()
    """     if kmir.bug_report is not None:
        new_input_file = Path(f'krun_inputs/{mir_file}')
        bug_report.add_file(mir_file, new_input_file)
        bug_report.add_command([a if a != str(mir_file) else str(new_input_file) for a in args]) """

    proc_res = kmir.interpret_mir_to_kore(proc_res.stdout, depth)

    kmir.print_kore_to_xxx(proc_res.stdout, output)
