from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cli.args import LoggingOptions

if TYPE_CHECKING:
    from typing import Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


@dataclass
class KMirOpts(LoggingOptions): ...


@dataclass
class RunOpts(KMirOpts):
    bin: str | None
    file: str | None
    depth: int
    start_symbol: str
    haskell_backend: bool


@dataclass
class ProofOpts(KMirOpts):
    proof_dir: Path
    id: str


@dataclass
class ProveOpts(KMirOpts):
    proof_dir: Path | None
    bug_report: Path | None
    max_depth: int | None
    max_iterations: int | None
    reload: bool

    def __init__(
        self,
        proof_dir: Path | str | None,
        bug_report: Path | None = None,
        max_depth: int | None = None,
        max_iterations: int | None = None,
        reload: bool = False,
    ) -> None:
        self.proof_dir = Path(proof_dir).resolve() if proof_dir is not None else None
        self.bug_report = bug_report
        self.max_depth = max_depth
        self.max_iterations = max_iterations
        self.reload = reload


@dataclass
class GenSpecOpts(KMirOpts):
    input_file: Path
    output_file: Path | None
    start_symbol: str

    def __init__(self, input_file: Path, output_file: Path | str | None, start_symbol: str) -> None:
        self.input_file = input_file
        if output_file is None:
            self.output_file = None
        else:
            self.output_file = Path(output_file).resolve()
        self.start_symbol = start_symbol


@dataclass
class ProveRSOpts(ProveOpts):
    rs_file: Path
    save_smir: bool
    smir: bool
    start_symbol: str

    def __init__(
        self,
        rs_file: Path,
        proof_dir: Path | str | None = None,
        bug_report: Path | None = None,
        max_depth: int | None = None,
        max_iterations: int | None = None,
        reload: bool = False,
        save_smir: bool = False,
        smir: bool = False,
        start_symbol: str = 'main',
    ) -> None:
        self.rs_file = rs_file
        self.proof_dir = Path(proof_dir).resolve() if proof_dir is not None else None
        self.bug_report = bug_report
        self.max_depth = max_depth
        self.max_iterations = max_iterations
        self.reload = reload
        self.save_smir = save_smir
        self.smir = smir
        self.start_symbol = start_symbol


@dataclass
class ProveRawOpts(ProveOpts):
    spec_file: Path
    include_labels: tuple[str, ...] | None
    exclude_labels: tuple[str, ...] | None

    def __init__(
        self,
        spec_file: Path,
        proof_dir: Path | str | None,
        include_labels: str | None = None,
        exclude_labels: str | None = None,
        bug_report: Path | None = None,
        max_depth: int | None = None,
        max_iterations: int | None = None,
        reload: bool = False,
    ) -> None:
        self.spec_file = spec_file
        self.proof_dir = Path(proof_dir).resolve() if proof_dir is not None else None
        self.include_labels = tuple(include_labels.split(',')) if include_labels is not None else None
        self.exclude_labels = tuple(exclude_labels.split(',')) if exclude_labels is not None else None
        self.bug_report = bug_report
        self.max_depth = max_depth
        self.max_iterations = max_iterations
        self.reload = reload


@dataclass
class DisplayOpts(ProofOpts):
    full_printer: bool
    smir_info: Path | None
    omit_current_body: bool

    def __init__(
        self,
        proof_dir: Path | str,
        id: str,
        full_printer: bool = True,
        smir_info: Path | None = None,
        omit_current_body: bool = True,
    ) -> None:
        self.proof_dir = Path(proof_dir).resolve() if proof_dir is not None else None
        self.id = id
        self.full_printer = full_printer
        self.smir_info = smir_info
        self.omit_current_body = omit_current_body


@dataclass
class ShowOpts(DisplayOpts): ...


@dataclass
class ViewOpts(DisplayOpts): ...


@dataclass
class PruneOpts(ProofOpts):
    node_id: int
