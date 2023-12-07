import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final, Optional
# from subprocess import CompletedProcess

# from pyk.ktool.kprint import KAstOutput, KPrint
# from pyk.kore.parser import KoreParser

from kmir import KMIR
from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)


def parse(
    kmir: KMIR,
    mir_file: Path,
    *,
    input: str = 'program', #TODO: support option `rs`
    output: str = 'pretty',
    temp_file: Optional[Path] = None,
) -> str:
    # input_format = KAstInput[input.upper()]
    # currently, 'program' is the default and only accepted input.
    
    if not temp_file:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = temp_file

    preprocess_mir_file(mir_file, temp_file)

    output_text = kmir.mir_to_k(temp_file, output).stdout

    return output_text



