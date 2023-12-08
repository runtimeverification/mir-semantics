import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final, Optional

from pyk.kore.parser import KoreParser
from pyk.kore.tools import PrintOutput, kore_print
from pyk.ktool.kprint import KAstOutput

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

    output_format = KAstOutput[output.upper()]

    proc_res = kmir.mir_to_k(temp_file)
    parse_to_kore_text = proc_res.stdout

    if output_format != KAstOutput.NONE:
        parse_to_kore = KoreParser(parse_to_kore_text).pattern()
        match output_format:
            case KAstOutput.JSON:
                print(kmir.kprint.kore_to_kast(parse_to_kore).to_json())
            case KAstOutput.KORE:
                print(parse_to_kore)
            case KAstOutput.PRETTY | KAstOutput.PROGRAM | KAstOutput.KAST | KAstOutput.BINARY | KAstOutput.LATEX:
                print(kore_print(parse_to_kore, kmir.llvm_dir, PrintOutput(output)))
                # TODO: Should use output_format
            case _:
                raise ValueError('Output format not supported.')
