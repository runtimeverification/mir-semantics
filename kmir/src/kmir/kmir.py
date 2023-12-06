__all__ = ['KMIR']

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final, final

from pyk.ktool.kprint import gen_glr_parser
from pyk.ktool.kprove import KProve
from pyk.utils import BugReport

_LOGGER: Final = logging.getLogger(__name__)


@final
@dataclass(frozen=True)
class KMIR:
    llvm_dir: Path
    haskell_dir: Path
    mir_parser: Path
    bug_report: BugReport | None
    kprove: KProve | None

    def __init__(
        self,
        llvm_dir: Path,
        haskell_dir: Path,
        bug_report: BugReport | None = None,
        use_directory: Path | None = None,
    ):
        mir_parser = llvm_dir / 'parser_Mir_MIR-SYNTAX'
        if not mir_parser.is_file():
            mir_parser = gen_glr_parser(mir_parser, definition_dir=llvm_dir, module='MIR-SYNTAX', sort='Mir')

        kprove = KProve(haskell_dir, use_directory=use_directory)

        object.__setattr__(self, 'llvm_dir', llvm_dir)
        object.__setattr__(self, 'haskell_dir', haskell_dir)
        object.__setattr__(self, 'mir_parser', mir_parser)
        object.__setattr__(self, 'bug_report', bug_report)
        object.__setattr__(self, 'kprove', kprove)
