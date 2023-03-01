from pathlib import Path
from subprocess import CalledProcessError

from pyk.cli_utils import run_process


def generate_mir_bison_parser(llvm_dir: Path, output_parser_file: Path) -> Path:
    """
    Invoke kast to generate a fast Bison parser

    TODO: upstearm to `kbuild`
    """
    try:
        kast_command = ['kast']
        kast_command += ['--definition', str(llvm_dir)]
        kast_command += ['--module', 'MIR-SYNTAX']
        kast_command += ['--sort', 'Mir']
        kast_command += ['--gen-glr-parser']
        kast_command += [str(output_parser_file)]
        run_process(kast_command)
        return output_parser_file
    except CalledProcessError as err:
        raise ValueError("Couldn't generate Bison parser") from err
