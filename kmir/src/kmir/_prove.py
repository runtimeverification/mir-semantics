from __future__ import annotations

import logging
import re
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm import CTerm
from pyk.kast.inner import KSequence, KVariable, Subst
from pyk.kast.manip import abstract_term_safely, split_config_from
from pyk.kcfg import KCFG
from pyk.kcfg.explore import KCFGExplore
from pyk.kore.rpc import BoosterServer, KoreClient
from pyk.proof.proof import parallel_advance_proof
from pyk.proof.reachability import APRProof, APRProver

from .cargo import cargo_get_smir_json
from .kast import SymbolicMode, make_call_config
from .kmir import KMIR, KMIRCTermSymbolic, KMIRSemantics, kore_server_logging_args
from .smir import SMIRInfo

if TYPE_CHECKING:
    from typing import Final

    from pyk.kast.inner import KInner

    from .options import ProveOpts


_LOGGER: Final = logging.getLogger(__name__)
_SUMMARY_TARGET_VAR_RE = re.compile(r'^(?P<base>[A-Z][A-Z0-9_]*?)_[0-9a-f]{8}(?:__kmir_q_\d+)?$')


def _canonicalize_summary_target_var_name(name: str) -> str:
    match = _SUMMARY_TARGET_VAR_RE.match(name)
    if match is None:
        return name
    return match.group('base')


def _make_stable_target_var(base_name: str, existing_names: set[str]) -> KVariable:
    name = base_name
    counter = 0
    while name in existing_names:
        counter += 1
        name = f'{base_name}_{counter}'
    existing_names.add(name)
    return KVariable(name)


def prove(opts: ProveOpts) -> APRProof:
    if not opts.rs_file.is_file():
        raise ValueError(f'Input file does not exist: {opts.rs_file}')

    if opts.max_workers is not None and opts.max_workers < 1:
        raise ValueError(f'Expected positive integer for `max_workers, got: {opts.max_workers}')

    # Sanitize label: K module names only allow alphanumeric + hyphen + underscore + dot.
    # Also truncate to avoid filesystem path length limits.
    import hashlib

    raw_label = f'{opts.rs_file.stem}.{opts.start_symbol}'
    label = ''.join(c if c.isalnum() or c in '._-' else '_' for c in raw_label)
    if len(label) > 200:
        digest = hashlib.sha256(raw_label.encode()).hexdigest()[:12]
        label = label[:200] + '_' + digest

    if opts.proof_dir is not None:
        target_path = opts.proof_dir / label
        return _prove(opts, target_path, label)

    with tempfile.TemporaryDirectory() as tmp_dir:
        target_path = Path(tmp_dir)
        return _prove(opts, target_path, label)


def _prove(opts: ProveOpts, target_path: Path, label: str) -> APRProof:
    if not opts.reload and opts.proof_dir is not None and APRProof.proof_data_exists(label, opts.proof_dir):
        _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {label}')
        proof = APRProof.read_proof_data(opts.proof_dir, label)

        smir_info = SMIRInfo.from_file(target_path / 'smir.json')
        kmir = KMIR.from_kompiled_kore(
            smir_info,
            target_dir=target_path,
            extra_modules=opts.add_modules or None,
            bug_report=opts.bug_report,
            symbolic=True,
            haskell_target=opts.haskell_target,
            llvm_lib_target=opts.llvm_lib_target,
            break_on_function=opts.break_on_function or None,
        )
    else:
        _LOGGER.info(f'Constructing initial proof: {label}')
        if opts.parsed_smir is not None:
            smir_info = SMIRInfo(opts.parsed_smir)
        elif opts.smir:
            smir_info = SMIRInfo.from_file(opts.rs_file)
        else:
            smir_info = SMIRInfo(cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir))

        smir_info = smir_info.reduce_to(opts.start_symbol)
        # Report whether the reduced call graph includes any functions without MIR bodies
        missing_body_syms = [
            sym
            for sym, item in smir_info.items.items()
            if 'MonoItemFn' in item['mono_item_kind'] and item['mono_item_kind']['MonoItemFn'].get('body') is None
        ]
        has_missing = len(missing_body_syms) > 0
        _LOGGER.info(f'Reduced items table size {len(smir_info.items)}')
        if has_missing:
            _LOGGER.info(f'missing-bodies-present={has_missing} count={len(missing_body_syms)}')
            _LOGGER.debug(f'Missing-body function symbols (first 5): {missing_body_syms[:5]}')

        kmir = KMIR.from_kompiled_kore(
            smir_info,
            target_dir=target_path,
            extra_modules=opts.add_modules or None,
            bug_report=opts.bug_report,
            symbolic=True,
            haskell_target=opts.haskell_target,
            llvm_lib_target=opts.llvm_lib_target,
            break_on_function=opts.break_on_function or None,
        )

        proof = apr_proof_from_smir(
            kmir,
            label,
            smir_info,
            start_symbol=opts.start_symbol,
            proof_dir=opts.proof_dir,
        )
        if proof.proof_dir is not None and (proof.proof_dir / label).is_dir():
            smir_info.dump(proof.proof_dir / proof.id / 'smir.json')

    if proof.passed:
        return proof

    cut_point_rules = _cut_point_rules(
        break_on_calls=opts.break_on_calls,
        break_on_function_calls=opts.break_on_function_calls,
        break_on_intrinsic_calls=opts.break_on_intrinsic_calls,
        break_on_thunk=opts.break_on_thunk or opts.terminate_on_thunk,  # must break for terminal rule
        break_every_statement=opts.break_every_statement,
        break_on_terminator_goto=opts.break_on_terminator_goto,
        break_on_terminator_switch_int=opts.break_on_terminator_switch_int,
        break_on_terminator_return=opts.break_on_terminator_return,
        break_on_terminator_call=opts.break_on_terminator_call,
        break_on_terminator_assert=opts.break_on_terminator_assert,
        break_on_terminator_drop=opts.break_on_terminator_drop,
        break_on_terminator_unreachable=opts.break_on_terminator_unreachable,
        break_every_terminator=opts.break_every_terminator,
        break_every_step=opts.break_every_step,
        break_on_function=opts.break_on_function,
    )

    if opts.max_workers and opts.max_workers > 1:
        _prove_parallel(kmir, proof, opts=opts, label=label, cut_point_rules=cut_point_rules)
    else:
        _prove_sequential(kmir, proof, opts=opts, label=label, cut_point_rules=cut_point_rules)
    return proof


def _prove_parallel(
    kmir: KMIR,
    proof: APRProof,
    *,
    opts: ProveOpts,
    label: str,
    cut_point_rules: list[str],
) -> None:
    assert opts.max_workers
    assert kmir.llvm_library_dir

    with BoosterServer(
        {
            'kompiled_dir': kmir.definition_dir,
            'llvm_kompiled_dir': kmir.llvm_library_dir,
            'module_name': kmir.definition.main_module_name,
            'bug_report': kmir.bug_report,
            'simplify_each': 30,
            'haskell_threads': opts.max_workers,
            **kore_server_logging_args(label),
        }
    ) as server:

        def create_prover() -> APRProver:
            client = KoreClient(
                'localhost',
                server.port,
                bug_report=kmir.bug_report,
                bug_report_id=label if kmir.bug_report is not None else None,
            )
            cterm_symbolic = KMIRCTermSymbolic(
                client,
                kmir.definition,
            )
            kcfg_explore = KCFGExplore(
                cterm_symbolic,
                kcfg_semantics=KMIRSemantics(terminate_on_thunk=opts.terminate_on_thunk),
            )
            prover = APRProver(
                kcfg_explore,
                execute_depth=opts.max_depth,
                cut_point_rules=cut_point_rules,
            )
            return prover

        started_at = time.perf_counter()
        try:
            parallel_advance_proof(
                proof,
                create_prover=create_prover,
                max_iterations=opts.max_iterations,
                max_workers=opts.max_workers,
                fail_fast=opts.fail_fast,
                maintenance_rate=opts.maintenance_rate,
            )
        finally:
            proof.add_exec_time(time.perf_counter() - started_at)
            proof.write_proof_data()


def _prove_sequential(
    kmir: KMIR,
    proof: APRProof,
    *,
    opts: ProveOpts,
    label: str,
    cut_point_rules: list[str],
) -> None:
    with kmir.kcfg_explore(label, terminate_on_thunk=opts.terminate_on_thunk) as kcfg_explore:
        prover = APRProver(
            kcfg_explore,
            execute_depth=opts.max_depth,
            cut_point_rules=cut_point_rules,
        )
        started_at = time.perf_counter()
        try:
            prover.advance_proof(
                proof,
                max_iterations=opts.max_iterations,
                fail_fast=opts.fail_fast,
                maintenance_rate=opts.maintenance_rate,
            )
        finally:
            proof.add_exec_time(time.perf_counter() - started_at)
            proof.write_proof_data()


def apr_proof_from_smir(
    kmir: KMIR,
    id: str,
    smir_info: SMIRInfo,
    *,
    start_symbol: str = 'main',
    proof_dir: Path | None = None,
    init_cterm: CTerm | None = None,
    target_k_cell: KInner | None = None,
) -> APRProof:
    """Create an APRProof for a KMIR function.

    If init_cterm is provided, use it as the initial state (for CSE normalized entry).
    Otherwise, construct from make_call_config (standard mode).
    """
    if init_cterm is not None:
        lhs = init_cterm
        lhs_config = init_cterm.config
    else:
        lhs_config, constraints = make_call_config(
            kmir.definition,
            smir_info=smir_info,
            start_symbol=start_symbol,
            mode=SymbolicMode(),
        )
        lhs = CTerm(lhs_config, constraints)

    var_config, var_subst = split_config_from(lhs_config)
    existing_rhs_var_names: set[str] = set()
    _rhs_subst: dict[str, KInner] = {}
    for v_name in var_subst:
        if target_k_cell is None:
            rhs_var = abstract_term_safely(KVariable('_'), base_name=v_name, existing_var_names=existing_rhs_var_names)
            existing_rhs_var_names.add(rhs_var.name)
        else:
            base_name = _canonicalize_summary_target_var_name(v_name)
            rhs_var = _make_stable_target_var(base_name, existing_rhs_var_names)
        _rhs_subst[v_name] = rhs_var
    _rhs_subst['K_CELL'] = target_k_cell if target_k_cell is not None else KSequence([KMIR.Symbols.END_PROGRAM])
    rhs = CTerm(Subst(_rhs_subst)(var_config))
    kcfg = KCFG()
    init_node = kcfg.create_node(lhs)
    target_node = kcfg.create_node(rhs)
    return APRProof(id, kcfg, [], init_node.id, target_node.id, {}, proof_dir=proof_dir)


def _cut_point_rules(
    *,
    break_on_calls: bool,
    break_on_function_calls: bool,
    break_on_intrinsic_calls: bool,
    break_on_thunk: bool,
    break_every_statement: bool,
    break_on_terminator_goto: bool,
    break_on_terminator_switch_int: bool,
    break_on_terminator_return: bool,
    break_on_terminator_call: bool,
    break_on_terminator_assert: bool,
    break_on_terminator_drop: bool,
    break_on_terminator_unreachable: bool,
    break_every_terminator: bool,
    break_every_step: bool,
    break_on_function: list[str] | None = None,
) -> list[str]:
    cut_point_rules = []
    if break_on_thunk:
        cut_point_rules.append('RT-DATA.thunk')
    if break_every_statement or break_every_step:
        cut_point_rules.extend(
            [
                'KMIR-CONTROL-FLOW.execStmt',
                'KMIR-CONTROL-FLOW.execStmt.union',
            ]
        )
    if break_on_terminator_goto or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termGoto')
    if break_on_terminator_switch_int or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termSwitchInt')
    if break_on_terminator_return or break_every_terminator or break_every_step:
        cut_point_rules.extend(
            [
                'KMIR-CONTROL-FLOW.termReturnSome',
                'KMIR-CONTROL-FLOW.termReturnNone',
                'KMIR-CONTROL-FLOW.endprogram-return',
                'KMIR-CONTROL-FLOW.endprogram-no-return',
            ]
        )
    if (
        break_on_intrinsic_calls
        or break_on_calls
        or break_on_terminator_call
        or break_every_terminator
        or break_every_step
    ):
        cut_point_rules.append('KMIR-CONTROL-FLOW.termCallIntrinsic')
    if (
        break_on_function_calls
        or break_on_calls
        or break_on_terminator_call
        or break_every_terminator
        or break_every_step
    ):
        cut_point_rules.append('KMIR-CONTROL-FLOW.termCallFunction')
    if break_on_function:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termCallFunctionFilter')
        cut_point_rules.append('KMIR-CONTROL-FLOW.termCallIntrinsicFilter')
    if break_on_terminator_assert or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termAssert')
    if break_on_terminator_drop or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termDrop')
    if break_on_terminator_unreachable or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termUnreachable')
    return cut_point_rules
