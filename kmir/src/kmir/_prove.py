from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm import CTerm
from pyk.cterm.symbolic import CTermSymbolic
from pyk.kast.inner import KSequence, KVariable, Subst
from pyk.kast.manip import abstract_term_safely, split_config_from
from pyk.kcfg import KCFG
from pyk.kcfg.explore import KCFGExplore
from pyk.kore.rpc import BoosterServer, KoreClient
from pyk.proof.proof import parallel_advance_proof
from pyk.proof.reachability import APRProof, APRProver

from .cargo import cargo_get_smir_json
from .kast import SymbolicMode, make_call_config
from .kmir import KMIR, KMIRSemantics
from .smir import SMIRInfo

if TYPE_CHECKING:
    from typing import Final

    from pyk.kast.inner import KInner

    from .options import ProveOpts


_LOGGER: Final = logging.getLogger(__name__)


def prove(opts: ProveOpts) -> list[APRProof]:
    """Prove one or more start symbols from the same file, kompiling only once."""
    if not opts.rs_file.is_file():
        raise ValueError(f'Input file does not exist: {opts.rs_file}')

    if opts.max_workers is not None and opts.max_workers < 1:
        raise ValueError(f'Expected positive integer for `max_workers, got: {opts.max_workers}')

    if opts.proof_dir is not None:
        if len(opts.start_symbols) == 1:
            label = f'{opts.rs_file.stem}.{opts.start_symbols[0]}'
            target_path = opts.proof_dir / label
        else:
            # Multiple start symbols share a separate target dir
            target_path = opts.proof_dir / f'{opts.rs_file.stem}.kompiled'
        return _prove_multi(opts, target_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        target_path = Path(tmp_dir)
        return _prove_multi(opts, target_path)


def prove_with_kmir(
    kmir: KMIR,
    smir_info: SMIRInfo,
    opts: ProveOpts,
) -> APRProof:
    """Prove a single symbol using a pre-built KMIR instance.

    The intended use case for this function is internal with the test runner.
    Use this instead of `prove()` when the caller manages kompilation externally
    (e.g. the test harness kompiles once and loops over symbols). Only the first
    entry in `opts.start_symbols` is used; for multi-symbol proving use `prove()`
    which kompiles once internally but is for external use via `kmir prove`.
    """
    assert len(opts.start_symbols) == 1, f'prove_with_kmir handles a single symbol; got {len(opts.start_symbols)}.'

    if opts.max_workers is not None and opts.max_workers < 1:
        raise ValueError(f'Expected positive integer for `max_workers, got: {opts.max_workers}')

    # No check for rs_file as smir_info already exists
    start_symbol = opts.start_symbols[0]
    label = f'{opts.rs_file.stem}.{start_symbol}'

    _LOGGER.info(f'Using pre-built KMIR for proof: {label}')
    proof = apr_proof_from_smir(
        kmir,
        label,
        smir_info,
        start_symbol=start_symbol,
        proof_dir=opts.proof_dir,
    )
    if opts.proof_dir is not None:
        kompiled_smir_path = opts.proof_dir / f'{opts.rs_file.stem}.kompiled' / 'smir.json'
        kompiled_smir_path.parent.mkdir(parents=True, exist_ok=True)
        smir_info.dump(kompiled_smir_path)

    return _advance_proof(kmir, proof, opts, label)


def _prove_multi(opts: ProveOpts, target_path: Path) -> list[APRProof]:
    """Prove single or multiple symbols with a single kompilation."""
    labels = [f'{opts.rs_file.stem}.{sym}' for sym in opts.start_symbols]

    if not labels:
        raise ValueError('No label to prove')

    # Check which proofs can be resumed
    resumable: dict[str, APRProof] = {}
    if not opts.reload and opts.proof_dir is not None:
        for label in labels:
            if APRProof.proof_data_exists(label, opts.proof_dir):
                _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {label}')
                resumable[label] = APRProof.read_proof_data(opts.proof_dir, label)

    # Load SMIR info (once)
    kompiled_smir_path = target_path / 'smir.json'
    if len(resumable) == len(labels):
        # All proofs are resumed, load SMIR from saved data
        smir_info = SMIRInfo.from_file(kompiled_smir_path)
    else:
        # Need fresh SMIR for at least one proof
        if opts.parsed_smir is not None:
            smir_info = SMIRInfo(opts.parsed_smir)
        elif opts.smir:
            smir_info = SMIRInfo.from_file(opts.rs_file)
        else:
            smir_info = SMIRInfo(cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir))

        smir_info = smir_info.reduce_to(opts.start_symbols)
        # Report whether the reduced call graph includes any functions without MIR bodies
        missing_body_syms = [
            sym
            for sym, item in smir_info.items.items()
            if 'MonoItemFn' in item['mono_item_kind'] and item['mono_item_kind']['MonoItemFn'].get('body') is None
        ]
        has_missing = len(missing_body_syms) > 0
        if has_missing:
            _LOGGER.info(f'missing-bodies-present={has_missing} count={len(missing_body_syms)}')
            _LOGGER.debug(f'Missing-body function symbols (first 5): {missing_body_syms[:5]}')

    kmir = KMIR.from_kompiled_kore(
        smir_info,
        target_dir=target_path,
        extra_module=opts.add_module,
        bug_report=opts.bug_report,
        symbolic=True,
        haskell_target=opts.haskell_target,
        llvm_lib_target=opts.llvm_lib_target,
        break_on_function=opts.break_on_function or None,
    )

    smir_info.dump(kompiled_smir_path)

    # Prove each symbol sequentially using shared definition
    results: list[APRProof] = []
    for label, start_symbol in zip(labels, opts.start_symbols, strict=True):
        if label in resumable:
            proof = resumable[label]
        else:
            _LOGGER.info(f'Constructing initial proof: {label}')
            proof = apr_proof_from_smir(
                kmir,
                label,
                smir_info,
                start_symbol=start_symbol,
                proof_dir=opts.proof_dir,
            )

        proof = _advance_proof(kmir, proof, opts, label)
        results.append(proof)

    return results


def _advance_proof(kmir: KMIR, proof: APRProof, opts: ProveOpts, label: str) -> APRProof:
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
        }
    ) as server:

        def create_prover() -> APRProver:
            client = KoreClient(
                'localhost',
                server.port,
                bug_report=kmir.bug_report,
                bug_report_id=label if kmir.bug_report is not None else None,
            )
            cterm_symbolic = CTermSymbolic(
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

        parallel_advance_proof(
            proof,
            create_prover=create_prover,
            max_iterations=opts.max_iterations,
            max_workers=opts.max_workers,
            fail_fast=opts.fail_fast,
            maintenance_rate=opts.maintenance_rate,
        )


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
        prover.advance_proof(
            proof,
            max_iterations=opts.max_iterations,
            fail_fast=opts.fail_fast,
            maintenance_rate=opts.maintenance_rate,
        )


def apr_proof_from_smir(
    kmir: KMIR,
    id: str,
    smir_info: SMIRInfo,
    *,
    start_symbol: str = 'main',
    proof_dir: Path | None = None,
) -> APRProof:
    lhs_config, constraints = make_call_config(
        kmir.definition,
        smir_info=smir_info,
        start_symbol=start_symbol,
        mode=SymbolicMode(),
    )
    lhs = CTerm(lhs_config, constraints)

    var_config, var_subst = split_config_from(lhs_config)
    _rhs_subst: dict[str, KInner] = {
        v_name: abstract_term_safely(KVariable('_'), base_name=v_name) for v_name in var_subst
    }
    _rhs_subst['K_CELL'] = KSequence([KMIR.Symbols.END_PROGRAM])
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
        cut_point_rules.append('KMIR-CONTROL-FLOW.termCallFunctionFilterMatch')
    if break_on_terminator_assert or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termAssert')
    if break_on_terminator_drop or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termDrop')
    if break_on_terminator_unreachable or break_every_terminator or break_every_step:
        cut_point_rules.append('KMIR-CONTROL-FLOW.termUnreachable')
    return cut_point_rules
