import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final, Optional

from .kmir import KMIR
from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)

def parse(
    kmir: KMIR,
    mir_file: Path,
    *,
    input: str = 'program',  # Assume 'program' only, TODO: support option `rs`
    output: str = 'none',
    temp_file: Optional[Path] = None,
) -> None:
    # input_format = KAstInput[input.upper()]
    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = temp_file

    preprocess_mir_file(mir_file, temp_file)

    proc_res = kmir.mir_to_kore(temp_file)

    kmir.print_kore_to_xxx(proc_res.stdout, output)
