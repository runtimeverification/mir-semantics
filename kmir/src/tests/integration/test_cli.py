from __future__ import annotations

import json
from pathlib import Path

import pytest

from kmir.__main__ import _kmir_info, _kmir_link, _kmir_prune, _kmir_show
from kmir.kmir import KMIR
from kmir.options import InfoOpts, LinkOpts, ProveRSOpts, PruneOpts, ShowOpts
from kmir.smir import SMIRInfo
from kmir.testing.fixtures import assert_or_update_show_output


PROVE_RS_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)


def _prove_and_store(kmir: KMIR, rs_or_json: Path, tmp_path: Path, start_symbol: str = 'main', is_smir: bool = False):
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
        out_custom, PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.cli-custom-printer.expected', update=update_expected_output
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
        out_default, PROVE_RS_DIR / f'show/{rs_file.stem}.{start_symbol}.cli-default-printer.expected', update=update_expected_output
    )


def test_cli_info_snapshot(capsys: pytest.CaptureFixture[str], update_expected_output: bool) -> None:
    smir_json = PROVE_RS_DIR / 'arith.smir.json'
    smir_info = SMIRInfo.from_file(smir_json)
    # choose first few type ids deterministically
    chosen_tys = sorted(list(smir_info.types.keys()))[:3]
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
        PROVE_RS_DIR / f"show/link.{smir1.stem}+{smir2.stem}.counts.expected",
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


