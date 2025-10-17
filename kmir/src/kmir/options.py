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
        full_printer: bool = False,
        smir_info: Path | None = None,
        omit_current_body: bool = True,
    ) -> None:
        self.proof_dir = Path(proof_dir).resolve() if proof_dir is not None else None
        self.id = id
        self.full_printer = full_printer
        self.smir_info = smir_info
        self.omit_current_body = omit_current_body


@dataclass
class ShowOpts(DisplayOpts):
    nodes: tuple[int, ...] | None
    node_deltas: tuple[tuple[int, int], ...] | None
    node_deltas_pro: tuple[tuple[int, int], ...] | None
    rules: tuple[tuple[int, int], ...] | None
    omit_cells: tuple[str, ...] | None
    omit_static_info: bool
    use_default_printer: bool
    statistics: bool
    leaves: bool

    def __init__(
        self,
        proof_dir: Path | str,
        id: str,
        full_printer: bool = False,
        smir_info: Path | None = None,
        omit_current_body: bool = True,
        nodes: str | None = None,
        node_deltas: str | None = None,
        node_deltas_pro: str | None = None,
        rules: str | None = None,
        omit_cells: str | None = None,
        omit_static_info: bool = True,
        use_default_printer: bool = False,
        statistics: bool = False,
        leaves: bool = False,
    ) -> None:
        super().__init__(proof_dir, id, full_printer, smir_info, omit_current_body)
        self.omit_static_info = omit_static_info
        self.use_default_printer = use_default_printer
        self.statistics = statistics
        self.leaves = leaves
        self.nodes = tuple(int(n.strip()) for n in nodes.split(',')) if nodes is not None else None

        def _parse_pairs(text: str | None) -> tuple[tuple[int, int], ...] | None:
            if text is None:
                return None
            pairs: list[tuple[int, int]] = []
            for delta in text.split(','):
                parts = delta.strip().split(':')
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    pairs.append((int(parts[0].strip()), int(parts[1].strip())))
            return tuple(pairs)

        self.node_deltas = _parse_pairs(node_deltas)
        self.node_deltas_pro = _parse_pairs(node_deltas_pro)
        self.rules = _parse_pairs(rules)

        static_info_cells = ('<functions>', '<start-symbol>', '<types>', '<adt-to-ty>')

        user_omit_cells = tuple(cell.strip() for cell in omit_cells.split(',')) if omit_cells is not None else ()

        if omit_static_info:
            self.omit_cells = static_info_cells + user_omit_cells
        else:
            self.omit_cells = user_omit_cells if user_omit_cells else None


@dataclass
class ViewOpts(DisplayOpts): ...


@dataclass
class PruneOpts(ProofOpts):
    node_id: int


@dataclass
class InfoOpts(KMirOpts):
    smir_file: Path
    types: tuple[int, ...] | None

    def __init__(self, smir_file: Path, types: str | None = None) -> None:
        self.smir_file = smir_file
        self.types = tuple(int(t.strip()) for t in types.split(',')) if types is not None else None


@dataclass
class LinkOpts(KMirOpts):
    smir_files: list[Path]
    output_file: Path

    def __init__(self, smir_files: list[str], output_file: str | None = None) -> None:
        self.smir_files = [Path(f) for f in smir_files]
        self.output_file = Path(output_file) if output_file is not None else Path('linker_output.smir.json')
