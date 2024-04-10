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
        llvm_dir_str = os.getenv('KMIR_LLVM_DIR')
        llvm_dir = Path(llvm_dir_str) if llvm_dir_str is not None else None
        return {
            'definition_dir': llvm_dir,
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
