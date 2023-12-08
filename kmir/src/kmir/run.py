# import logging

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from pyk.kore.parser import KoreParser
from pyk.kore.tools import PrintOutput, kore_print
from pyk.ktool.krun import KRunOutput

from .kmir import KMIR
from .utils import preprocess_mir_file


def run(
    kmir: KMIR,
    mir_file: Path,
    *,
    depth: int | None = None,
    output: str = 'none',
    temp_file: Optional[Path] = None,
) -> None:
    if temp_file is None:
        with NamedTemporaryFile(mode='w') as f:
            temp_file = Path(f.name)
    else:
        temp_file = Path(temp_file)

    preprocess_mir_file(mir_file, temp_file)

    parse_to_kore_text = kmir.mir_to_k(mir_file).stdout
    parse_to_kore = KoreParser(parse_to_kore_text).pattern()

    # TODO: We could enable more options like krun, refer to https://github.com/runtimeverification/pyk/blob/bb20d0e27e438b224034b1ada86ee205753065b5/src/pyk/ktool/krun.py#L183

    # TODO: what should we do to the bug_report, reference pyk.ktools.krun._krun()
    """     if kmir.bug_report is not None:
        new_input_file = Path(f'krun_inputs/{mir_file}')
        bug_report.add_file(mir_file, new_input_file)
        bug_report.add_command([a if a != str(mir_file) else str(new_input_file) for a in args]) """

    proc_res = kmir.interpret_mir_to_kore(parse_to_kore, depth)
    run_result_kore_text = proc_res.stdout

    output_format = KRunOutput(output)
    if output_format != KRunOutput.NONE:
        run_result_kore = KoreParser(run_result_kore_text).pattern()
        match output_format:
            case KRunOutput.JSON:
                print(kmir.kprint.kore_to_kast(run_result_kore).to_json())
            case KRunOutput.KORE:
                print(run_result_kore)
            case KRunOutput.PRETTY | KRunOutput.PROGRAM | KRunOutput.KAST | KRunOutput.LATEX | KRunOutput.BINARY:
                print(kore_print(run_result_kore, kmir.llvm_dir, PrintOutput(output)))
                # TODO: Should use output_format
            case _:
                raise ValueError('Output format not supported.')
