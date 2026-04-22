from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kmir.__main__ import _kmir_show
from kmir.cse import CSESummaryStore
from kmir.kmir import KMIR
from kmir.options import ProveOpts, ShowOpts
from kmir.testing.fixtures import assert_or_update_show_output

if TYPE_CHECKING:
    import pytest

    from pyk.cterm import CTerm
    from pyk.proof.reachability import APRProof

PROVE_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)


def test_cse_branch_summary_expected_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    rs_file = PROVE_DIR / 'cse-branch-summary.rs'
    summary_store = tmp_path / 'summary-store'

    stages = [
        ('partial_caller0', False, 1),
        ('partial_caller1', False, 1),
        ('partial_caller2', True, 2),
        ('caller', True, 2),
    ]
    for start_symbol, expected_complete, expected_outcomes in stages:
        base = _prove(
            rs_file,
            tmp_path / f'branch-{start_symbol}-base',
            start_symbol=start_symbol,
        )
        proof = _prove(
            rs_file,
            tmp_path / f'branch-{start_symbol}',
            start_symbol=start_symbol,
            cse_function='classify',
            summary_store=summary_store,
        )
        summary = _summary(summary_store, 'classify')
        assert summary.complete is expected_complete
        assert len(summary.outcomes) == expected_outcomes
        assert not proof.kcfg.ndbranches()
        assert any(rule.startswith('CSE.summary.classify') for edge in proof.kcfg.edges() for rule in edge.rules)
        _assert_final_states_equal(base, proof)
        _assert_show(
            proof.proof_dir,
            proof.id,
            PROVE_DIR / f'show/cse-branch-summary.{start_symbol}.cse.expected',
            capsys,
            update_expected_output,
        )


def test_cse_reference_argument_summary_reuse(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    base = _prove(
        PROVE_DIR / 'cse-reference-summary.rs',
        tmp_path / 'reference-base',
        start_symbol='caller',
    )
    proof = _prove(
        PROVE_DIR / 'cse-reference-summary.rs',
        tmp_path / 'reference-reuse',
        start_symbol='caller',
        cse_function='read_nested_ref',
        summary_store=tmp_path / 'reference-summary-store',
    )
    summary = _summary(tmp_path / 'reference-summary-store', 'read_nested_ref')
    assert summary.complete
    assert len(summary.outcomes) == 1
    assert not proof.kcfg.ndbranches()
    assert any(rule.startswith('CSE.summary.read_nested_ref') for edge in proof.kcfg.edges() for rule in edge.rules)
    _assert_final_states_equal(base, proof)
    _assert_show(
        proof.proof_dir,
        proof.id,
        PROVE_DIR / 'show/cse-reference-summary.caller.cse.expected',
        capsys,
        update_expected_output,
    )


def _prove(
    rs_file: Path,
    proof_dir: Path,
    *,
    start_symbol: str,
    cse_function: str | None = None,
    summary_store: Path | None = None,
):
    opts = ProveOpts(
        rs_file,
        proof_dir=proof_dir,
        start_symbols=[start_symbol],
        cse_functions=[cse_function] if cse_function else [],
        cse_summary_store=summary_store,
        reload=True,
    )
    proof = KMIR.prove_program(opts)
    proof.write_proof_data()
    return proof


def _summary(summary_store: Path, function: str):
    summary = CSESummaryStore(summary_store).load(function)
    assert summary is not None
    return summary


def _assert_final_states_equal(base: APRProof, cse: APRProof) -> None:
    assert base.passed
    assert cse.passed
    assert _final_state_keys(base) == _final_state_keys(cse)


def _final_state_keys(proof: APRProof) -> tuple[CTerm, ...]:
    covers = proof.kcfg.covers(target_id=proof.target)
    assert covers
    return tuple(sorted(cover.source.cterm for cover in covers))


def _assert_show(
    proof_dir: Path | None,
    proof_id: str,
    expected_file: Path,
    capsys: pytest.CaptureFixture[str],
    update: bool,
) -> None:
    assert proof_dir is not None
    _kmir_show(
        ShowOpts(
            proof_dir=proof_dir,
            id=proof_id,
            full_printer=False,
            smir_info=None,
            omit_current_body=False,
            use_default_printer=False,
        )
    )
    out = capsys.readouterr().out.rstrip()
    assert_or_update_show_output(out, expected_file, update=update)
