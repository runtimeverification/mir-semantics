from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kast.manip import remove_generated_cells
from pyk.kast.outer import KRule

from .kmir import KMIR
from .smir import SMIRInfo, Ty

if TYPE_CHECKING:
    from typing import Final

    from pyk.proof.reachability import APRProof

    from .options import ProveOpts


_LOGGER: Final = logging.getLogger(__name__)


@dataclass
class CSEResult:
    """Result of a CSE (Compositional Symbolic Execution) pipeline run."""

    summaries: dict[str, Path] = field(default_factory=dict)
    summary_times: dict[str, float] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    final_proof: APRProof | None = None
    final_prove_time: float = 0.0

    def summary_report(self) -> str:
        lines = ['=== CSE Summary ===']
        if self.summaries:
            lines.append(f'Generated {len(self.summaries)} function summaries:')
            for name, path in self.summaries.items():
                t = self.summary_times.get(name, 0.0)
                lines.append(f'  {name}: {t:.1f}s -> {path}')
        if self.skipped:
            lines.append(f'Skipped {len(self.skipped)} functions:')
            for name, reason in self.skipped.items():
                lines.append(f'  {name}: {reason}')
        if self.final_proof is not None:
            lines.append(
                f'Final proof: {"PASSED" if self.final_proof.passed else "FAILED"} ({self.final_prove_time:.1f}s)'
            )
        return '\n'.join(lines)


def write_to_module(kmir: KMIR, proof: APRProof, to_module_path: Path) -> None:
    """Write proof KCFG as a K module to the specified path."""
    module_name = proof.id.upper().replace('.', '-').replace('_', '-') + '-SUMMARY'
    k_module = proof.kcfg.to_module(module_name=module_name, defunc_with=kmir.definition)

    if to_module_path.suffix == '.json':
        to_module_path.write_text(json.dumps(k_module.to_dict(), indent=2))
    else:

        def _process_sentence(sent):  # type: ignore[no-untyped-def]
            if isinstance(sent, KRule):
                sent = sent.let(body=remove_generated_cells(sent.body))
            return sent

        k_module_readable = k_module.let(sentences=[_process_sentence(sent) for sent in k_module.sentences])
        k_module_text = kmir.pretty_print(k_module_readable)
        to_module_path.write_text(k_module_text)
    _LOGGER.info(f'Module written to: {to_module_path}')


def _topological_sort(call_edges: dict[Ty, set[Ty]], root: Ty) -> list[Ty]:
    """Return callees of root in reverse topological order (leaves first).

    Cycles are broken by skipping back-edges (the function in the cycle
    that causes the back-edge is simply omitted from the order).
    The root itself is excluded from the result.
    """
    order: list[Ty] = []
    visited: set[Ty] = set()
    in_stack: set[Ty] = set()

    def dfs(node: Ty) -> None:
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for callee in call_edges.get(node, set()):
            if callee in in_stack:
                continue  # back-edge, skip to break cycle
            if callee not in visited:
                dfs(callee)
        in_stack.discard(node)
        order.append(node)

    dfs(root)
    # Remove root itself — we don't want to summarize the target function
    if order and order[-1] == root:
        order.pop()
    return order  # leaves first, which is what we want


def _ty_to_name(smir_info: SMIRInfo, ty: Ty) -> str | None:
    """Map a Ty ID back to a human-readable function name."""
    sym = smir_info.function_symbols.get(int(ty))
    if sym is None:
        return None
    if 'NormalSym' in sym:
        normal_sym = sym['NormalSym']
        # Look up the item to get the short name
        if normal_sym in smir_info.items:
            item = smir_info.items[normal_sym]
            if SMIRInfo._is_func(item):
                return item['mono_item_kind']['MonoItemFn']['name']
        return normal_sym
    if 'IntrinsicSym' in sym:
        return sym['IntrinsicSym']
    return None


def _has_body(smir_info: SMIRInfo, ty: Ty) -> bool:
    """Check if a function has a MIR body (not an intrinsic or extern)."""
    sym = smir_info.function_symbols.get(int(ty))
    if sym is None:
        return False
    if 'IntrinsicSym' in sym:
        return False
    if 'NormalSym' not in sym:
        return False
    normal_sym = sym['NormalSym']
    if normal_sym not in smir_info.items:
        return False
    item = smir_info.items[normal_sym]
    if not SMIRInfo._is_func(item):
        return False
    body = item['mono_item_kind']['MonoItemFn'].get('body')
    return body is not None


def _sanitize_filename(name: str) -> str:
    """Convert a function name to a safe filename."""
    return name.replace('::', '__').replace('<', '_').replace('>', '_').replace(' ', '_')


def cse_prove(opts: ProveOpts) -> CSEResult:
    """Compositional Symbolic Execution pipeline.

    1. Parse SMIR, extract call graph
    2. Topologically sort callees (bottom-up)
    3. For each callee: prove, minimize, export summary
    4. Re-prove target with all summaries
    """
    from ._prove import prove
    from .cargo import cargo_get_smir_json

    result = CSEResult()

    # Parse SMIR
    if opts.parsed_smir is not None:
        smir_info = SMIRInfo(opts.parsed_smir)
    elif opts.smir:
        smir_info = SMIRInfo.from_file(opts.rs_file)
    else:
        smir_info = SMIRInfo(cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir))

    # Determine summary directory
    summary_dir = opts.summary_dir
    if summary_dir is None:
        if opts.proof_dir is not None:
            summary_dir = opts.proof_dir / 'summaries'
        else:
            summary_dir = Path.cwd() / 'summaries'
    summary_dir.mkdir(parents=True, exist_ok=True)

    # Get root function Ty
    start_name = opts.start_symbol
    if start_name not in smir_info.function_tys:
        raise ValueError(
            f'Start symbol {start_name!r} not found in SMIR. Available: {list(smir_info.function_tys.keys())[:10]}'
        )
    root_ty = Ty(smir_info.function_tys[start_name])

    # Topological sort of callees
    callee_order = _topological_sort(smir_info.call_edges, root_ty)
    _LOGGER.info(f'CSE: {len(callee_order)} callees to summarize for {start_name}')

    # Phase 1: Generate summaries for each callee
    for ty in callee_order:
        name = _ty_to_name(smir_info, ty)
        if name is None:
            _LOGGER.debug(f'CSE: skipping Ty({ty}) — cannot resolve name')
            continue

        if not _has_body(smir_info, ty):
            _LOGGER.debug(f'CSE: skipping {name} — no MIR body (intrinsic or extern)')
            result.skipped[name] = 'no MIR body'
            continue

        safe_name = _sanitize_filename(name)
        summary_path = summary_dir / f'{safe_name}.json'

        # Check cache
        if summary_path.exists() and not opts.reload:
            print(f'[CSE] {name}: using cached summary {summary_path}')
            result.summaries[name] = summary_path
            result.summary_times[name] = 0.0
            continue

        # Check if the function is provable (exists in function_tys)
        if name not in smir_info.function_tys:
            _LOGGER.debug(f'CSE: skipping {name} — not in function_tys')
            result.skipped[name] = 'not in function_tys'
            continue

        print(f'[CSE] {name}: proving...', flush=True)
        t0 = time.time()

        try:
            # Build ProveOpts for this callee
            from .options import ProveOpts as ProveOptsClass

            callee_proof_dir = opts.proof_dir / 'cse-callee-proofs' if opts.proof_dir else None
            if callee_proof_dir:
                callee_proof_dir.mkdir(parents=True, exist_ok=True)

            # Collect already-generated summaries for this callee's own callees
            available_summaries = [p for p in result.summaries.values() if p.exists()]

            callee_opts = ProveOptsClass(
                rs_file=opts.rs_file,
                proof_dir=callee_proof_dir,
                haskell_target=opts.haskell_target,
                llvm_lib_target=opts.llvm_lib_target,
                bug_report=opts.bug_report,
                max_depth=opts.max_depth,
                max_iterations=opts.max_iterations,
                reload=opts.reload,
                fail_fast=True,
                maintenance_rate=opts.maintenance_rate,
                save_smir=opts.save_smir,
                smir=opts.smir,
                parsed_smir=smir_info._smir,
                start_symbol=name,
                add_modules=available_summaries,
            )

            proof = prove(callee_opts)
            elapsed = time.time() - t0

            if not proof.passed:
                print(f'[CSE] {name}: proof FAILED in {elapsed:.1f}s, skipping summary')
                result.skipped[name] = f'proof failed ({elapsed:.1f}s)'
                continue

            # Minimize and export
            proof.minimize_kcfg()

            from pyk.kdist import kdist

            kmir = KMIR(
                definition_dir=kdist.which(opts.haskell_target or 'mir-semantics.haskell'),
                llvm_library_dir=kdist.which(opts.llvm_lib_target or 'mir-semantics.llvm-library'),
            )
            write_to_module(kmir, proof, summary_path)

            result.summaries[name] = summary_path
            result.summary_times[name] = elapsed
            print(f'[CSE] {name}: proved in {elapsed:.1f}s, exported to {summary_path}')

        except Exception as e:
            elapsed = time.time() - t0
            _LOGGER.warning(f'CSE: failed to prove {name}: {e}', exc_info=True)
            result.skipped[name] = f'error: {e}'
            print(f'[CSE] {name}: ERROR in {elapsed:.1f}s — {e}')

    # Phase 2: Prove the main target with all summaries
    all_summary_paths = [p for p in result.summaries.values() if p.exists()]
    # Also include any user-provided modules
    all_modules = list(opts.add_modules) + all_summary_paths

    print(f'[CSE] Proving {start_name} with {len(all_summary_paths)} summaries...', flush=True)
    t0 = time.time()

    from .options import ProveOpts as ProveOptsClass

    final_opts = ProveOptsClass(
        rs_file=opts.rs_file,
        proof_dir=opts.proof_dir,
        haskell_target=opts.haskell_target,
        llvm_lib_target=opts.llvm_lib_target,
        bug_report=opts.bug_report,
        max_depth=opts.max_depth,
        max_iterations=opts.max_iterations,
        max_workers=opts.max_workers,
        reload=opts.reload,
        fail_fast=opts.fail_fast,
        maintenance_rate=opts.maintenance_rate,
        save_smir=opts.save_smir,
        smir=opts.smir,
        parsed_smir=smir_info._smir,
        start_symbol=start_name,
        add_modules=all_modules,
        break_on_calls=opts.break_on_calls,
        break_on_function_calls=opts.break_on_function_calls,
        break_on_intrinsic_calls=opts.break_on_intrinsic_calls,
        break_on_thunk=opts.break_on_thunk,
        terminate_on_thunk=opts.terminate_on_thunk,
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

    final_proof = prove(final_opts)
    result.final_prove_time = time.time() - t0
    result.final_proof = final_proof
    print(f'[CSE] {start_name}: {"PASSED" if final_proof.passed else "FAILED"} in {result.final_prove_time:.1f}s')

    return result
