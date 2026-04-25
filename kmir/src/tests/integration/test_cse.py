from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from pyk.cterm import CTerm
from pyk.cterm.symbolic import CTermExecute
from pyk.kast.inner import KApply, KRewrite, KSequence, KVariable
from pyk.kast.prelude.ml import mlEqualsTrue, mlTop
from pyk.kast.outer import KRule
from pyk.kcfg import KCFG
from pyk.kcfg.kcfg import Step
from pyk.proof.reachability import APRProof

from kmir.__main__ import _kmir_show
from kmir.cse import CSECallInfo, CSEOutcome, CSERuntime, CSESummary, CSESummaryStore, summary_from_proof
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
        expected_outcomes=1,
    ),
    CSECase(
        id='branch-partial-caller1',
        rs_file='cse-branch-summary.rs',
        start_symbol='partial_caller1',
        cse_function='classify',
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
    CSECase(
        id='double-reference-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='double_ref_caller',
        cse_function='write_double_ref',
    ),
    CSECase(
        id='double-pointer-caller',
        rs_file='cse-reference-summary.rs',
        start_symbol='double_ptr_caller',
        cse_function='write_double_ptr',
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


def test_cse_summary_updates_when_existing_initial_is_too_strong(
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
    assert len(summary.outcomes) == 1
    assert summary.outcomes[0].metadata['kind'] == 'covered'
    assert summary.outcomes[0].final == covered.cterm


def test_cse_summary_moves_initial_constraints_to_guards() -> None:
    kcfg = KCFG()
    init_constraint = mlEqualsTrue(KVariable('CSE_INIT_CONSTRAINT'))
    init = kcfg.create_node(CTerm(_test_cell('init'), (init_constraint,)))
    final = kcfg.create_node(CTerm(_test_cell('target'), (init_constraint,)))
    target = kcfg.create_node(CTerm(_test_cell('target')))
    kcfg.create_edge(init.id, final.id, 1, rules=['return-rule'])
    kcfg.create_cover(final.id, target.id)
    proof = APRProof('cse-summary-initial-constraints-in-guards', kcfg, [], init.id, target.id, {})

    summary = summary_from_proof('callee', proof)

    assert summary is not None
    assert summary.initial.constraints == ()
    assert summary.outcomes[0].final.constraints == ()
    assert summary.outcomes[0].guard == init_constraint


def test_cse_summary_serialization_omits_derived_complete() -> None:
    kcfg = KCFG()
    init = kcfg.create_node(CTerm(_test_cell('init')))
    target = kcfg.create_node(CTerm(_test_cell('target')))
    final = kcfg.create_node(CTerm(_test_cell('target')))
    kcfg.create_edge(init.id, final.id, 1, rules=['return-rule'])
    kcfg.create_cover(final.id, target.id)
    proof = APRProof('cse-summary-no-complete-field', kcfg, [], init.id, target.id, {})

    summary = summary_from_proof('callee', proof)

    assert summary is not None
    assert 'complete' not in summary.to_dict()
    assert type(summary).from_dict(summary.to_dict()) == summary


def test_cse_summary_apply_uses_stored_backend_rule() -> None:
    post_k = KApply('#execBlockIdx(_)_KMIR-CONTROL-FLOW_KItem_BasicBlockIdx', (KApply('target'),))
    post_state = CTerm.from_kast(_k_cell(post_k))
    rule = KRule(KRewrite(_test_cell('caller'), _k_cell(post_k)))
    summary = CSESummary(
        function='callee',
        initial=CTerm(_locals_cell()),
        outcomes=(CSEOutcome(guard=mlTop(), final=CTerm(_return_cell()), metadata={}, rule=rule),),
        source={},
    )

    class Store:
        def load(self, function: str) -> CSESummary | None:
            assert function == 'callee'
            return summary

        def save(self, summary: CSESummary) -> None:
            raise AssertionError('existing applicable summary should not be regenerated')

    class Symbolic:
        added_modules: list[tuple[str, bool]] = []
        executed_modules: list[tuple[int | None, str | None]] = []

        def add_module(self, module, name_as_id: bool = False) -> str:
            self.added_modules.append((module.name, name_as_id))
            return module.name

        def execute(self, cterm, depth=None, cut_point_rules=None, terminal_rules=None, module_name=None):
            self.executed_modules.append((depth, module_name))
            return CTermExecute(
                state=post_state,
                next_states=(),
                depth=1,
                vacuous=False,
                logs=(),
            )

    runtime = CSERuntime(
        functions=['callee'],
        store=Store(),  # type: ignore[arg-type]
        kmir=None,  # type: ignore[arg-type]
        opts=None,  # type: ignore[arg-type]
        proof_label='test',
    )
    runtime.target_call_info = lambda _cterm: CSECallInfo(  # type: ignore[method-assign]
        function='callee',
        args=(),
        destination=KApply('dest'),
        target=KApply('someBasicBlockIdx_BODY_MaybeBasicBlockIdx', (KApply('target'),)),
    )
    runtime.generate_summary = lambda *_args: None  # type: ignore[method-assign]

    symbolic = Symbolic()
    result = runtime.custom_step(CTerm(_test_cell('caller')), symbolic)  # type: ignore[arg-type]

    assert isinstance(result, Step)
    assert len(symbolic.added_modules) == 1
    module_name, name_as_id = symbolic.added_modules[0]
    assert module_name.startswith('CSE-SUMMARY-CALLEE-')
    assert name_as_id
    assert symbolic.executed_modules == [(1, module_name)]
    assert result.rule_labels == ['CSE.summary.callee']


def _test_cell(name: str) -> KApply:
    return KApply('<top>', (KApply(name),))


def _k_cell(item: KApply) -> KApply:
    return KApply('<top>', (KApply('<k>', (KSequence([item]),)),))


def _return_cell() -> KApply:
    return KApply('<top>', (KApply('<retval>', (KApply('noReturn_BODY_ReturnVal'),)),))


def _locals_cell() -> KApply:
    return KApply('<top>', (KApply('<locals>', (KApply('ListItem', (KApply('local0'),)),)),))


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
