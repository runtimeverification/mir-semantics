import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Final, Optional

from pyk.cli.args import LoggingOptions

from .kmir import KMIR
from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


class ParseOptions(LoggingOptions):
    mir_file: Path
    definition_dir: Path | None
    input: str
    output: str

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'definition_dir': os.getenv('KMIR_LLVM_DIR'),
            'input': 'program',
            'output': 'pretty',
        }


def parse(
    kmir: KMIR,
    options: ParseOptions,
    *,
    temp_file: Optional[Path] = None,
) -> None:
    # input_format = KAstInput[input.upper()]
    _LOGGER.info(f'Parsing {options.mir_file} from format {options.input} to format {options.output}')

    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)

    preprocess_mir_file(options.mir_file, temp_file)

    proc_res = kmir.mir_to_kore(temp_file)

    kmir.print_kore_to_xxx(proc_res.stdout, options.output)
