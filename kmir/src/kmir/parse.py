import logging
import subprocess
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from tempfile import NamedTemporaryFile
from typing import Final, Optional, Union

from pyk.cli.utils import check_file_path
from pyk.ktool.kprint import KAstOutput, gen_glr_parser

from .utils import preprocess_mir_file

_LOGGER: Final = logging.getLogger(__name__)


def parse(
    llvm_dir: Path,
    mir_file: Path,
    #   input: str,
    output: str,
    # log: Logger,
    temp_file: Optional[Union[str, Path]] = None,
) -> CompletedProcess:
    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = Path(temp_file)

    preprocess_mir_file(mir_file, temp_file)

    # input_format = KAstInput[input.upper()]
    output_format = KAstOutput[output.upper()]

    mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'
    if not mir_parser.is_file():
        mir_parser = gen_glr_parser(mir_parser, definition_dir=llvm_dir, module='MIR-SYNTAX', sort='Mir')

    # other input format? How should we deal with it
    kore_output = mir_to_k(mir_parser, temp_file)

    match output_format:
        case KAstOutput.KORE:
            return kore_output.stdout
       # case KAstOutput.PRETTY:
        case _:
            return kore_output
    # TODO: kore convert to other output format? Move to Main?
    # return kore_output.stdout


def mir_to_k(
    parser: Path,
    program_file: Path,
    # input: KAstInput,
) -> CompletedProcess:
    try:
        command = [str(parser)] + [str(program_file)]
        proc_res = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)
    except CalledProcessError as err:
        raise ValueError("Couldn't parse program") from err
    return proc_res
