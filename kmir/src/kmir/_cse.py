from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kast.manip import remove_generated_cells
from pyk.kast.outer import KRule
from pyk.proof.reachability import APRProof

from .kmir import KMIR
from .smir import SMIRInfo, Ty

if TYPE_CHECKING:
    from typing import Final

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

    @property
    def total_callee_time(self) -> float:
        return sum(self.summary_times.values())

    @property
    def total_time(self) -> float:
        return self.total_callee_time + self.final_prove_time

    def summary_report(self) -> str:
        lines = ['=== CSE Summary ===']
        if self.summaries:
            lines.append(f'Callee summaries ({len(self.summaries)}, total {self.total_callee_time:.1f}s):')
            for name, path in self.summaries.items():
                t = self.summary_times.get(name, 0.0)
                lines.append(f'  {name}: {t:.1f}s -> {path}')
        if self.skipped:
            lines.append(f'Skipped {len(self.skipped)} functions:')
            for name, reason in self.skipped.items():
                lines.append(f'  {name}: {reason}')
        if self.final_proof is not None:
            status = 'PASSED' if self.final_proof.passed else 'FAILED'
            lines.append(f'Main proof: {status} ({self.final_prove_time:.1f}s)')
            lines.append(
                f'Total: {self.total_time:.1f}s (callees {self.total_callee_time:.1f}s + main {self.final_prove_time:.1f}s)'
            )
        return '\n'.join(lines)


def write_to_module(kmir: KMIR, proof: APRProof, to_module_path: Path) -> None:
    """Write proof KCFG as a K module to the specified path."""
    # Sanitize module name: K identifiers only allow alphanumeric + hyphen
    raw_name = proof.id.upper().replace('.', '-').replace('_', '-')
    module_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in raw_name) + '-SUMMARY'
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
    """Convert a function name to a safe filename, truncated to fit filesystem limits."""
    import hashlib

    safe = name.replace('::', '__').replace('<', '_').replace('>', '_').replace(' ', '_')
    safe = ''.join(c if c.isalnum() or c in '_-' else '_' for c in safe)
    # Filesystem limit is 255 bytes; leave room for .json extension + hash suffix
    max_base = 200
    if len(safe) > max_base:
        digest = hashlib.sha256(name.encode()).hexdigest()[:12]
        safe = safe[:max_base] + '_' + digest
    return safe


def cse_prove(opts: ProveOpts) -> CSEResult:
    """Compositional Symbolic Execution pipeline.

    1. Parse SMIR, extract call graph
    2. Topologically sort callees (bottom-up)
    3. For each callee: prove, minimize, export summary
    4. Re-prove target with all summaries
    """
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

        print(f'[CSE] {name}: proving (normalized entry)...', flush=True)
        t0 = time.time()

        try:
            available_summaries = [p for p in result.summaries.values() if p.exists()]

            callee_proof_dir = opts.proof_dir / 'cse-callee-proofs' if opts.proof_dir else None
            if callee_proof_dir:
                callee_proof_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Build KMIR with function tables for this callee
            callee_smir = smir_info.reduce_to(name)
            callee_target = callee_proof_dir / safe_name if callee_proof_dir else Path(f'/tmp/cse-{safe_name}')
            kmir_callee = KMIR.from_kompiled_kore(
                callee_smir,
                target_dir=callee_target,
                extra_modules=available_summaries or None,
                bug_report=opts.bug_report,
                symbolic=True,
                haskell_target=opts.haskell_target,
                llvm_lib_target=opts.llvm_lib_target,
            )

            # Step 2: Create synthetic init state and execute call setup to normalized entry
            from .kast import SymbolicMode, make_call_config

            init_config, init_constraints = make_call_config(
                kmir_callee.definition,
                smir_info=callee_smir,
                start_symbol=name,
                mode=SymbolicMode(),
            )
            from pyk.cterm import CTerm, cterm_symbolic

            init_cterm = CTerm(init_config, init_constraints)

            with cterm_symbolic(
                kmir_callee.definition,
                kmir_callee.definition_dir,
                llvm_definition_dir=kmir_callee.llvm_library_dir,
                bug_report=kmir_callee.bug_report,
            ) as cts:
                # Execute call setup step-by-step until #execBlock is in <k>
                normalized = init_cterm
                setup_depth = 0
                for _step in range(30):
                    result_cterm, _next, depth, _vacuous, _logs = cts.execute(normalized, depth=1)
                    if depth == 0:
                        if _next:
                            normalized = _next[0].state
                            setup_depth += 1
                        else:
                            break  # stuck
                    else:
                        normalized = result_cterm
                        setup_depth += 1

                    # Check if K cell starts with #execBlock
                    k = normalized.cell('K_CELL')
                    from pyk.kast.inner import KApply as _KApp
                    from pyk.kast.inner import KSequence as _KSeq

                    first = k.items[0] if isinstance(k, _KSeq) and k.items else k
                    if isinstance(first, _KApp) and '#execBlock(' in first.label.name:
                        break

                if setup_depth == 0:
                    _LOGGER.warning(f'CSE: call setup made no progress for {name}')
                    result.skipped[name] = 'setup stuck'
                    continue

            _LOGGER.info(f'CSE: normalized entry in {setup_depth} steps for {name}')

            # Step 3: Create proof from normalized entry (not synthetic init)
            from ._prove import _prove_sequential, apr_proof_from_smir

            callee_label = f'{opts.rs_file.stem}.{name}'
            import hashlib as _hashlib

            raw_label = callee_label
            callee_label = ''.join(c if c.isalnum() or c in '._-' else '_' for c in raw_label)
            if len(callee_label) > 200:
                digest = _hashlib.sha256(raw_label.encode()).hexdigest()[:12]
                callee_label = callee_label[:200] + '_' + digest

            proof = apr_proof_from_smir(
                kmir_callee,
                callee_label,
                callee_smir,
                start_symbol=name,
                proof_dir=callee_proof_dir,
                init_cterm=normalized,
            )
            if callee_proof_dir:
                callee_smir.dump(callee_proof_dir / callee_label / 'smir.json')

            # Step 4: Run the prover
            if not proof.passed:
                from .options import ProveOpts as ProveOptsClass

                callee_opts = ProveOptsClass(
                    rs_file=opts.rs_file,
                    max_depth=opts.max_depth,
                    max_iterations=opts.max_iterations,
                )
                _prove_sequential(
                    kmir_callee,
                    proof,
                    opts=callee_opts,
                    label=callee_label,
                    cut_point_rules=[],
                )

            elapsed = time.time() - t0

            # Check if the proof has any successful paths (cover edges to target)
            covers = [c for c in proof.kcfg.covers() if c.target.id == proof.target]
            stuck_nodes = [n for n in proof.kcfg.leaves if proof.kcfg.is_stuck(n.id)]

            if not covers:
                print(f'[CSE] {name}: no successful paths in {elapsed:.1f}s, skipping summary')
                result.skipped[name] = f'no covers ({elapsed:.1f}s)'
                continue

            status_str = 'PASSED' if proof.passed else f'PARTIAL ({len(covers)} paths ok, {len(stuck_nodes)} stuck)'
            print(f'[CSE] {name}: {status_str} in {elapsed:.1f}s', flush=True)

            # Export summaries from successful paths (even if some paths are stuck)
            proof.minimize_kcfg()

            from pyk.kdist import kdist

            kmir = KMIR(
                definition_dir=kdist.which(opts.haskell_target or 'mir-semantics.haskell'),
                llvm_library_dir=kdist.which(opts.llvm_lib_target or 'mir-semantics.llvm-library'),
            )
            write_to_module(kmir, proof, summary_path)

            result.summaries[name] = summary_path
            result.summary_times[name] = elapsed
            print(f'[CSE] {name}: exported {len(covers)} path summaries to {summary_path}')

        except Exception as e:
            elapsed = time.time() - t0
            _LOGGER.warning(f'CSE: failed to prove {name}: {e}', exc_info=True)
            result.skipped[name] = f'error: {e}'
            print(f'[CSE] {name}: ERROR in {elapsed:.1f}s — {e}')

    # Phase 2: Prove the main target with all summaries
    all_summary_paths = [p for p in result.summaries.values() if p.exists()]
    # Also include any user-provided modules
    all_modules = list(opts.add_modules) + all_summary_paths

    # Build callee_proofs map: function Ty -> APRProof (for CSE semantics)
    callee_proofs: dict[int, APRProof] = {}
    for callee_name, _summary_path in result.summaries.items():
        # Load the callee proof if it exists
        callee_proof_dir_path = opts.proof_dir / 'cse-callee-proofs' if opts.proof_dir else None
        if callee_proof_dir_path:
            import hashlib as _hashlib

            raw_label = f'{opts.rs_file.stem}.{callee_name}'
            callee_label = ''.join(c if c.isalnum() or c in '._-' else '_' for c in raw_label)
            if len(callee_label) > 200:
                digest = _hashlib.sha256(raw_label.encode()).hexdigest()[:12]
                callee_label = callee_label[:200] + '_' + digest
            if APRProof.proof_data_exists(callee_label, callee_proof_dir_path):
                callee_proof = APRProof.read_proof_data(callee_proof_dir_path, callee_label)
                # Accept proofs with any cover edges (not just fully passed)
                has_covers = any(c.target.id == callee_proof.target for c in callee_proof.kcfg.covers())
                if has_covers:
                    if callee_name in smir_info.function_tys:
                        func_ty = smir_info.function_tys[callee_name]
                        callee_proofs[func_ty] = callee_proof
                        _LOGGER.info(f'CSE: loaded callee proof for {callee_name} (ty={func_ty})')

    print(
        f'[CSE] Proving {start_name} with {len(callee_proofs)} dynamic summaries '
        f'+ {len(all_summary_paths)} module summaries...',
        flush=True,
    )
    t0 = time.time()

    # Build the proof with CSE semantics for dynamic interception
    from ._prove import apr_proof_from_smir

    main_smir = smir_info.reduce_to(start_name)
    kmir = KMIR.from_kompiled_kore(
        main_smir,
        target_dir=opts.proof_dir / f'{opts.rs_file.stem}.{start_name}' if opts.proof_dir else Path('/tmp/cse-main'),
        extra_modules=all_modules or None,
        bug_report=opts.bug_report,
        symbolic=True,
        haskell_target=opts.haskell_target,
        llvm_lib_target=opts.llvm_lib_target,
    )

    final_proof = apr_proof_from_smir(
        kmir,
        f'{opts.rs_file.stem}.{start_name}',
        main_smir,
        start_symbol=start_name,
        proof_dir=opts.proof_dir,
    )
    if opts.proof_dir:
        main_smir.dump(opts.proof_dir / final_proof.id / 'smir.json')

    if not final_proof.passed:
        from .kmir import KMIRCSESemantics
        from .options import ProveOpts as ProveOptsClass

        # Use CSE semantics with callee proofs for dynamic function call interception
        cse_semantics = KMIRCSESemantics(
            callee_proofs=callee_proofs,
            terminate_on_thunk=opts.terminate_on_thunk,
        )

        from pyk.cterm import cterm_symbolic as _cterm_symbolic
        from pyk.kcfg.explore import KCFGExplore
        from pyk.proof.reachability import APRProver

        with _cterm_symbolic(
            kmir.definition,
            kmir.definition_dir,
            llvm_definition_dir=kmir.llvm_library_dir,
            bug_report=kmir.bug_report,
            simplify_each=30,
        ) as cts:
            kcfg_explore = KCFGExplore(cts, kcfg_semantics=cse_semantics)
            # Use termCallFunction as cut-point so the backend stops at function calls.
            # After the cut, <k> has #execTerminatorCall(Ty, FUNC, ARGS, DEST, TARGET, UNWIND, SPAN).
            # custom_step recognizes this pattern (Pattern 2 in _extract_call_info).
            # Note: we use existing rule labels to avoid adding new ones to kmir.md
            # (which can cause LLVM backend compilation order changes).
            cse_cut_points = [
                'KMIR-CONTROL-FLOW.termCallFunction',
                'KMIR-CONTROL-FLOW.termCallFunctionFilter',
            ]
            prover = APRProver(
                kcfg_explore,
                execute_depth=opts.max_depth,
                cut_point_rules=cse_cut_points,
                # fast_check_subsumption=True,  # TODO: re-enable after debugging subsumption
            )
            prover.advance_proof(
                final_proof,
                max_iterations=opts.max_iterations or 1000,
                fail_fast=opts.fail_fast,
                maintenance_rate=opts.maintenance_rate,
            )

    result.final_prove_time = time.time() - t0
    result.final_proof = final_proof
    print(f'[CSE] {start_name}: {"PASSED" if final_proof.passed else "FAILED"} in {result.final_prove_time:.1f}s')

    return result
