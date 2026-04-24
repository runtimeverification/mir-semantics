from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from pyk.cterm import CTerm
from pyk.kast.inner import KApply
from pyk.kcfg import KCFG
from pyk.proof.reachability import APRProof

from kmir.__main__ import _kmir_show
from kmir.cse import CSESummaryStore, summary_from_proof
from kmir.kmir import KMIR
from kmir.options import ProveOpts, ShowOpts
from kmir.testing.fixtures import assert_or_update_show_output

PROVE_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)


@dataclass(frozen=True)
class CSECase:
    id: str
    rs_file: str
    start_symbol: str
    cse_function: str
    expected_complete: bool = True
    expected_outcomes: int = 1
    expected_splits: int = 0
    seed_start_symbol: str | None = None
    show_expected: str | None = None


CSE_BRANCH_STAGES = [
    CSECase(
        id='branch-partial-caller0',
        rs_file='cse-branch-summary.rs',
        start_symbol='partial_caller0',
        cse_function='classify',
        expected_complete=False,
        expected_outcomes=1,
    ),
    CSECase(
        id='branch-partial-caller1',
        rs_file='cse-branch-summary.rs',
        start_symbol='partial_caller1',
        cse_function='classify',
        expected_complete=False,
        expected_outcomes=1,
    ),
    CSECase(
        id='branch-partial-caller2',
        rs_file='cse-branch-summary.rs',
        start_symbol='partial_caller2',
        cse_function='classify',
        expected_outcomes=2,
    ),
    CSECase(
        id='branch-caller',
        rs_file='cse-branch-summary.rs',
        start_symbol='caller',
        cse_function='classify',
        expected_outcomes=2,
        expected_splits=1,
    ),
]


CSE_REFERENCE_CASES = [
    CSECase(
        id='reference-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='caller',
        cse_function='read_nested_ref',
    ),
    CSECase(
        id='reference-projected-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='projected_caller',
        cse_function='read_nested_ref',
        seed_start_symbol='caller',
    ),
    CSECase(
        id='mutable-reference-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='mutable_caller',
        cse_function='write_nested_ref',
    ),
    CSECase(
        id='nested-struct-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='nested_struct_caller',
        cse_function='write_struct_ref',
    ),
    CSECase(
        id='disjoint-field-reference-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='pair_fields_caller',
        cse_function='write_pair_fields',
    ),
    CSECase(
        id='tuple-contained-reference-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='tuple_ref_caller',
        cse_function='write_tuple_ref',
    ),
    CSECase(
        id='pointer-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='ptr_caller',
        cse_function='write_ptr',
    ),
]


def test_cse_branch_summary_expected_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    summary_store = tmp_path / 'summary-store'

    for case in CSE_BRANCH_STAGES:
        _assert_cse_case(case, tmp_path, summary_store, capsys, update_expected_output)


def test_cse_partial_summary_with_covered_and_remainder(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    summary_store = tmp_path / 'summary-store'

    _prove(
        PROVE_DIR / 'cse-branch-summary.rs',
        tmp_path / 'branch-partial-seed',
        start_symbol='partial_caller0',
        cse_function='classify',
        summary_store=summary_store,
    )
    summary = _summary(summary_store, 'classify')
    assert not summary.complete
    assert len(summary.outcomes) == 1

    _assert_cse_case(
        CSECase(
            id='branch-mixed',
            rs_file='cse-branch-summary.rs',
            start_symbol='caller',
            cse_function='classify',
            expected_outcomes=2,
            expected_splits=1,
            show_expected='cse-branch-summary.caller.partial-cse.expected',
        ),
        tmp_path,
        summary_store,
        capsys,
        update_expected_output,
    )


def test_cse_summary_from_failed_proof_keeps_frontier() -> None:
    kcfg = KCFG()
    init = kcfg.create_node(CTerm(_test_cell('init')))
    target = kcfg.create_node(CTerm(_test_cell('target')))
    stuck = kcfg.create_node(CTerm(_test_cell('stuck')))
    kcfg.create_edge(init.id, stuck.id, 1, rules=['stuck-rule'])
    kcfg.add_stuck(stuck.id)
    proof = APRProof('cse-summary-stuck-frontier', kcfg, [], init.id, target.id, {})

    summary = summary_from_proof('callee', proof)

    assert summary is not None
    assert not proof.passed
    assert summary.complete
    assert summary.source['proof_status'] == 'failed'
    assert len(summary.outcomes) == 1
    assert summary.outcomes[0].metadata['kind'] == 'stuck'


def test_cse_summary_extracts_covered_frontier_source() -> None:
    kcfg = KCFG()
    init = kcfg.create_node(CTerm(_test_cell('init')))
    covered = kcfg.create_node(CTerm(_test_cell('covered')))
    target = kcfg.create_node(CTerm(_test_cell('covered')))
    kcfg.create_edge(init.id, covered.id, 1, rules=['return-rule'])
    kcfg.create_cover(covered.id, target.id)
    proof = APRProof('cse-summary-covered-frontier', kcfg, [], init.id, target.id, {})

    assert not proof.kcfg.is_leaf(covered.id)
    summary = summary_from_proof('callee', proof)

    assert summary is not None
    assert proof.passed
    assert summary.complete
    assert len(summary.outcomes) == 1
    assert summary.outcomes[0].metadata['kind'] == 'covered'
    assert summary.outcomes[0].final == covered.cterm


def _test_cell(name: str) -> KApply:
    return KApply('<top>', (KApply(name),))


@pytest.mark.parametrize('case', CSE_REFERENCE_CASES, ids=[case.id for case in CSE_REFERENCE_CASES])
def test_cse_reference_and_pointer_cases(
    case: CSECase,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    _assert_cse_case(case, tmp_path, tmp_path / f'{case.id}-summary-store', capsys, update_expected_output)


def _assert_cse_case(
    case: CSECase,
    tmp_path: Path,
    summary_store: Path,
    capsys: pytest.CaptureFixture[str],
    update_expected_output: bool,
) -> None:
    rs_file = PROVE_DIR / case.rs_file

    if case.seed_start_symbol is not None:
        seed = _prove(
            rs_file,
            tmp_path / f'{case.id}-seed',
            start_symbol=case.seed_start_symbol,
            cse_function=case.cse_function,
            summary_store=summary_store,
        )
        assert _has_summary_rule(seed, case.cse_function)

    base = _prove(
        rs_file,
        tmp_path / f'{case.id}-base',
        start_symbol=case.start_symbol,
    )
    proof = _prove(
        rs_file,
        tmp_path / f'{case.id}-cse',
        start_symbol=case.start_symbol,
        cse_function=case.cse_function,
        summary_store=summary_store,
    )

    summary = _summary(summary_store, case.cse_function)
    assert summary.complete is case.expected_complete
    assert len(summary.outcomes) == case.expected_outcomes
    assert len(proof.kcfg.splits()) == case.expected_splits
    assert not proof.kcfg.ndbranches()
    assert _has_summary_rule(proof, case.cse_function)
    _assert_final_states_equal(base, proof)
    _assert_show(
        proof.proof_dir,
        proof.id,
        _show_expected_file(case),
        capsys,
        update_expected_output,
    )


def _show_expected_file(case: CSECase) -> Path:
    show_file = case.show_expected or f'{Path(case.rs_file).stem}.{case.start_symbol}.cse.expected'
    return PROVE_DIR / 'show' / show_file


def _has_summary_rule(proof: APRProof, function: str) -> bool:
    return any(rule.startswith(f'CSE.summary.{function}') for edge in proof.kcfg.edges() for rule in edge.rules)


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
