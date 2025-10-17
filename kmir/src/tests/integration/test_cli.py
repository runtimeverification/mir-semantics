from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from kmir.__main__ import _kmir_info, _kmir_link, _kmir_prune, _kmir_show
from kmir.options import InfoOpts, LinkOpts, ProveRSOpts, PruneOpts, ShowOpts
from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output
from kmir.utils import render_statistics
from pyk.cterm import CTerm
from pyk.kcfg.kcfg import KCFG

if TYPE_CHECKING:
    import pytest
    from pyk.proof import APRProof

    from kmir.kmir import KMIR

PROVE_RS_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)


class _FakeProof:
    def __init__(self, kcfg: KCFG, init_id: int, target_id: int) -> None:
        self.kcfg = kcfg
        self.init = init_id
        self._target_ids = {target_id}
        self._terminal_ids = {target_id}

    def is_target(self, node_id: int) -> bool:
        return node_id in self._target_ids

    def is_terminal(self, node_id: int) -> bool:
        return node_id in self._terminal_ids

    def is_refuted(self, node_id: int) -> bool:
        return False

    def is_bounded(self, node_id: int) -> bool:
        return False

    def is_pending(self, node_id: int) -> bool:
        return False

    def is_failing(self, node_id: int) -> bool:
        return False


def _prove_and_store(
    kmir: KMIR, rs_or_json: Path, tmp_path: Path, start_symbol: str = 'main', is_smir: bool = False
) -> APRProof:
    opts = ProveRSOpts(rs_or_json, proof_dir=tmp_path, smir=is_smir, start_symbol=start_symbol)
    apr_proof = kmir.prove_rs(opts)
    apr_proof.write_proof_data()
    return apr_proof


def test_cli_show_printers_snapshot(
    kmir: KMIR, tmp_path: Path, capsys: pytest.CaptureFixture[str], update_expected_output: bool
) -> None:
    rs_file = PROVE_RS_DIR / 'assert-true.rs'
    start_symbol = 'main'
    apr_proof = _prove_and_store(kmir, rs_file, tmp_path, start_symbol=start_symbol, is_smir=False)

    # Custom KMIRPrettyPrinter
    show_opts_custom = ShowOpts(
        proof_dir=tmp_path,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=False,
        use_default_printer=False,
    )
    _kmir_show(show_opts_custom)
    out_custom = capsys.readouterr().out.rstrip()
    assert_or_update_show_output(
        out_custom,
        PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.cli-custom-printer.expected',
        update=update_expected_output,
    )

    # Standard PrettyPrinter
    show_opts_default = ShowOpts(
        proof_dir=tmp_path,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=False,
        use_default_printer=True,
    )
    _kmir_show(show_opts_default)
    out_default = capsys.readouterr().out.rstrip()
    assert_or_update_show_output(
        out_default,
        PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.cli-default-printer.expected',
        update=update_expected_output,
    )


def test_cli_show_statistics_and_leaves(
    kmir: KMIR, tmp_path: Path, capsys: pytest.CaptureFixture[str], update_expected_output: bool
) -> None:
    rs_file = PROVE_RS_DIR / 'symbolic-args-fail.rs'
    start_symbol = 'main'
    apr_proof = _prove_and_store(kmir, rs_file, tmp_path, start_symbol=start_symbol, is_smir=False)

    show_opts = ShowOpts(
        proof_dir=tmp_path,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=False,
        use_default_printer=False,
        statistics=True,
        leaves=True,
    )
    _kmir_show(show_opts)
    out = capsys.readouterr().out.rstrip()

    assert_or_update_show_output(
        out,
        PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.cli-stats-leaves.expected',
        update=update_expected_output,
    )


def test_cli_statistics_lists_all_paths() -> None:
    """Ensure that statistics output enumerates every root-to-leaf path."""

    kcfg = KCFG()
    nodes = [kcfg.create_node(CTerm.top()) for _ in range(12)]

    root = nodes[0]
    mid1 = nodes[1]
    mid2 = nodes[2]
    branch_a = nodes[3]
    branch_b = nodes[4]
    post_a = nodes[5]
    post_b = nodes[6]
    a_leaf1 = nodes[7]
    a_leaf2 = nodes[8]
    b_leaf1 = nodes[9]
    b_leaf2 = nodes[10]
    target = nodes[11]

    kcfg.create_edge(root.id, mid1.id, depth=10)
    kcfg.create_edge(mid1.id, mid2.id, depth=20)
    kcfg.create_ndbranch(mid2.id, (branch_a.id, branch_b.id))

    kcfg.create_edge(branch_a.id, post_a.id, depth=30)
    kcfg.create_ndbranch(post_a.id, (a_leaf1.id, a_leaf2.id))
    kcfg.create_edge(branch_b.id, post_b.id, depth=40)
    kcfg.create_ndbranch(post_b.id, (b_leaf1.id, b_leaf2.id))

    kcfg.create_edge(a_leaf1.id, target.id, depth=50)
    kcfg.create_edge(a_leaf2.id, target.id, depth=51)
    kcfg.create_edge(b_leaf1.id, target.id, depth=60)
    kcfg.create_edge(b_leaf2.id, target.id, depth=61)

    proof = _FakeProof(kcfg, root.id, target.id)

    lines = render_statistics(proof)
    leaf_lines = [line for line in lines if line.startswith('  leaf ')]

    expected_paths = [
        (112, (root.id, mid1.id, mid2.id, branch_a.id, post_a.id, a_leaf1.id, target.id)),
        (113, (root.id, mid1.id, mid2.id, branch_a.id, post_a.id, a_leaf2.id, target.id)),
        (132, (root.id, mid1.id, mid2.id, branch_b.id, post_b.id, b_leaf1.id, target.id)),
        (133, (root.id, mid1.id, mid2.id, branch_b.id, post_b.id, b_leaf2.id, target.id)),
    ]

    assert len(leaf_lines) == len(expected_paths)

    actual_paths = []
    for line in leaf_lines:
        prefix, path_part = line.split(': steps ')
        steps_str, path_str = path_part.split(', path ')
        steps = int(steps_str)
        node_seq = tuple(int(node_id.strip()) for node_id in path_str.split(' -> '))
        actual_paths.append((steps, node_seq))
    actual_paths.sort()

    assert actual_paths == expected_paths
    assert '  total steps            : 112' in lines


def test_cli_info_snapshot(capsys: pytest.CaptureFixture[str], update_expected_output: bool) -> None:
    smir_json = PROVE_RS_DIR / 'arith.smir.json'
    smir_info = SMIRInfo.from_file(smir_json)
    # choose first few type ids deterministically
    chosen_tys = sorted(smir_info.types.keys())[:3]
    types_arg = ','.join(str(t) for t in chosen_tys)

    info_opts = InfoOpts(smir_file=smir_json, types=types_arg)
    _kmir_info(info_opts)
    out = capsys.readouterr().out.rstrip()
    assert_or_update_show_output(
        out, PROVE_RS_DIR / f'show/{smir_json.stem}.cli-info.expected', update=update_expected_output
    )


def test_cli_link_counts_snapshot(tmp_path: Path, update_expected_output: bool) -> None:
    smir1 = PROVE_RS_DIR / 'arith.smir.json'
    smir2 = (Path(__file__).parent / 'data' / 'exec-smir' / 'arithmetic' / 'unary.smir.json').resolve(strict=True)
    output_file = tmp_path / 'linked.smir.json'

    link_opts = LinkOpts(smir_files=[str(smir1), str(smir2)], output_file=str(output_file))
    _kmir_link(link_opts)

    linked = json.loads(output_file.read_text())
    counts_text = '\n'.join(
        [
            f"name: {linked['name']}",
            f"types: {len(linked['types'])}",
            f"functions: {len(linked['functions'])}",
            f"items: {len(linked['items'])}",
            f"spans: {len(linked['spans'])}",
        ]
    )

    assert_or_update_show_output(
        counts_text,
        PROVE_RS_DIR / f'show/link.{smir1.stem}+{smir2.stem}.counts.expected',
        update=update_expected_output,
    )


def test_cli_prune_snapshot(
    kmir: KMIR, tmp_path: Path, capsys: pytest.CaptureFixture[str], update_expected_output: bool
) -> None:
    rs_file = PROVE_RS_DIR / 'assert-true.rs'
    start_symbol = 'main'
    apr_proof = _prove_and_store(kmir, rs_file, tmp_path, start_symbol=start_symbol, is_smir=False)

    prune_opts = PruneOpts(proof_dir=tmp_path, id=apr_proof.id, node_id=apr_proof.target)
    _kmir_prune(prune_opts)
    out = capsys.readouterr().out.rstrip()
    assert_or_update_show_output(
        out, PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.cli-prune.expected', update=update_expected_output
    )
