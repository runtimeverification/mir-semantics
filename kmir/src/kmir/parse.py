import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final, Optional

from .kmir import KMIR
from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def parse(
    kmir: KMIR,
    mir_file: Path,
    *,
    input: str = 'program',  # Assume 'program' only, TODO: support option `rs`
    output: str = 'none',
    temp_file: Optional[Path] = None,
) -> None:
    # input_format = KAstInput[input.upper()]
    _LOGGER.info(f'Parsing {mir_file} from format {input} to format {output}')

    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)

    preprocess_mir_file(mir_file, temp_file)

    proc_res = kmir.mir_to_kore(temp_file)

    kmir.print_kore_to_xxx(proc_res.stdout, output)
