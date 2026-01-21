from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.__main__ import _kmir_info, _kmir_link, _kmir_prune, _kmir_show
from kmir.options import InfoOpts, LinkOpts, ProveRSOpts, PruneOpts, ShowOpts
from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output

if TYPE_CHECKING:
    from pyk.proof import APRProof

    from kmir.kmir import KMIR

PROVE_RS_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)


def _prove_and_store(
    kmir: KMIR,
    rs_or_json: Path,
    tmp_path: Path,
    start_symbol: str = 'main',
    is_smir: bool = False,
    max_depth: int | None = None,
) -> APRProof:
    opts = ProveRSOpts(rs_or_json, proof_dir=tmp_path, smir=is_smir, start_symbol=start_symbol, max_depth=max_depth)
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


@pytest.mark.parametrize(
    'src,start_symbol,is_smir',
    [
        pytest.param(
            (PROVE_RS_DIR / 'symbolic-args-fail.rs'),
            'main',
            False,
            id='symbolic-args-fail.main',
        ),
        pytest.param(
            (Path(__file__).parent / 'data' / 'exec-smir' / 'niche-enum' / 'niche-enum.smir.json').resolve(strict=True),
            'foo',
            True,
            id='niche-enum.smir.foo',
        ),
    ],
)
def test_cli_show_statistics_and_leaves(
    src: Path,
    start_symbol: str,
    is_smir: bool,
    kmir: KMIR,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    apr_proof = _prove_and_store(kmir, src, tmp_path, start_symbol=start_symbol, is_smir=is_smir)

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
        PROVE_RS_DIR / f'show/{src.stem}.{start_symbol}.cli-stats-leaves.expected',
        update=update_expected_output,
    )


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


def test_cli_show_to_module(
    kmir: KMIR, tmp_path: Path, capsys: pytest.CaptureFixture[str], update_expected_output: bool
) -> None:
    """Test --to-module option with both K text and JSON output formats."""
    rs_file = PROVE_RS_DIR / 'assert-true.rs'
    start_symbol = 'main'
    apr_proof = _prove_and_store(kmir, rs_file, tmp_path, start_symbol=start_symbol, is_smir=False)

    # Test K text output
    module_k_output = tmp_path / 'summary.k'
    show_opts_k = ShowOpts(
        proof_dir=tmp_path,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=True,
        use_default_printer=False,
        to_module=module_k_output,
    )
    _kmir_show(show_opts_k)
    capsys.readouterr()  # Clear captured output

    assert module_k_output.exists(), 'Module K file should be created'
    k_content = module_k_output.read_text()
    assert_or_update_show_output(
        k_content.rstrip(),
        PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.to-module.k',
        update=update_expected_output,
    )

    # Test JSON output (for --add-module)
    module_json_output = tmp_path / 'summary.json'
    show_opts_json = ShowOpts(
        proof_dir=tmp_path,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=True,
        use_default_printer=False,
        to_module=module_json_output,
    )
    _kmir_show(show_opts_json)
    capsys.readouterr()  # Clear captured output

    assert module_json_output.exists(), 'Module JSON file should be created'
    json_content = module_json_output.read_text()
    # Verify it's valid JSON
    json.loads(json_content)
    assert_or_update_show_output(
        json_content.rstrip(),
        PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.to-module.json',
        update=update_expected_output,
    )


def test_cli_show_minimize_proof(kmir: KMIR, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test --minimize-proof option."""
    rs_file = PROVE_RS_DIR / 'symbolic-args-fail.rs'
    start_symbol = 'main'
    # Use limited depth to create a partial proof with intermediate nodes that can be minimized
    apr_proof = _prove_and_store(kmir, rs_file, tmp_path, start_symbol=start_symbol, is_smir=False, max_depth=5)

    # Get initial node count
    from pyk.proof.reachability import APRProof

    initial_proof = APRProof.read_proof_data(tmp_path, apr_proof.id)
    initial_node_count = len(list(initial_proof.kcfg.nodes))

    # Run show with minimize_proof
    show_opts = ShowOpts(
        proof_dir=tmp_path,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=True,
        use_default_printer=False,
        minimize_proof=True,
    )
    _kmir_show(show_opts)
    capsys.readouterr()  # Clear captured output

    # Read the minimized proof
    minimized_proof = APRProof.read_proof_data(tmp_path, apr_proof.id)
    minimized_node_count = len(list(minimized_proof.kcfg.nodes))

    # Verify minimization reduced (or didn't increase) node count
    assert (
        minimized_node_count < initial_node_count
    ), f'Minimization should not increase node count: {minimized_node_count} > {initial_node_count}'


def test_cli_prove_rs_add_module(kmir: KMIR, tmp_path: Path) -> None:
    """Test --add-module option for prove-rs using stored module files."""
    from kmir.kmir import KMIR

    rs_file = PROVE_RS_DIR / 'assert-true.rs'
    start_symbol = 'main'

    # Use the stored JSON module file generated by --to-module
    stored_module_json = PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.to-module.json'
    assert stored_module_json.exists(), f'Stored JSON module file not found: {stored_module_json}'

    # Run prove-rs with --add-module and max_depth=1
    opts_with_module = ProveRSOpts(
        rs_file,
        proof_dir=tmp_path,
        smir=False,
        start_symbol=start_symbol,
        max_depth=1,
        add_module=stored_module_json,
    )
    proof_with_module = KMIR.prove_rs(opts_with_module)

    # With depth=1, we should have 3 nodes: init, one step, target
    assert len(list(proof_with_module.kcfg.nodes)) == 3
