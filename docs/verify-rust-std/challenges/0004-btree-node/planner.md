# Planner Record: Challenge 0004

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0004-btree-node.md
- Tracking issue: [#77](https://github.com/model-checking/verify-rust-std/issues/77)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0004-btree-node`
- Generator record: `docs/verify-rust-std/challenges/0004-btree-node/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0004-btree-node/evaluator.md`

## Requirements Extraction

- Published goal: verify the memory safety of `alloc::collections::btree::node` in the published Rust std snapshot, with particular attention to the unsafe-heavy node and handle APIs that underpin `BTreeMap`.
- Published success criteria: cover the public functions listed in the challenge page, especially the safe entry points that contain unsafe code, and prove the recursive or loop-based functions unbounded rather than with fixed-depth bounds.
- Challenge-specific UB obligations: rule out dangling or misaligned loads/stores, uninitialized reads, mutation of immutable bytes, and creation or use of invalid values in every proof that touches this module.
- Additional safety conditions from source docs or SAFETY comments: preserve uniform tree depth, preserve the `n keys / n values / n + 1 edges` node shape, keep internal nodes initialized with at least one valid edge, and respect the borrow-mode-specific invariants called out in `node.rs` for parent links, reborrows, deallocation, and root-level promotion or demotion.

## Scope Contract

- In scope for current branch: define the verification slice for this challenge, enumerate the module-level invariants, map every published success-criterion function to a planned proof or harness, and record the minimal evidence needed for a later generator/evaluator pass.
- Out of scope unless later justified: editing the standard-library implementation, changing generator/evaluator/rubric files, broadening to unrelated `alloc` or `collections` modules, or introducing cross-repo dependencies that are not required by the challenge page.
- Exceptional dependency escalation policy: any need to touch a secondary repository, refresh the stdlib snapshot, or widen the tool chain must be logged here and in the generator/evaluator records before it is treated as part of scope.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Requirements extraction and artifact alignment | Published goal, success criteria, UB obligations, and assumptions are recorded in planner and reflected in the local README | complete |
| 1 | Function coverage map | Each listed public function is assigned a planned proof or explicit blocker, with safe-vs-unsafe entry points separated | planned |
| 2 | Core node invariants | The node-shape, parent-link, and borrow-mode assumptions are reduced to a reusable contract for the generator phase | planned |
| 3 | Recursive and loop-based obligations | The unbounded functions are identified with their termination or induction strategy and any solver-risk notes | planned |
| 4 | Cross-check and handoff | Dependencies, blockers, and reuse candidates are stable enough for generator and evaluator follow-up | planned |

## Dependencies And Blockers

- Upstream challenge wording is the source of truth; any mismatch with local branch context must be resolved against the published page before planning further work.
- Proof scope is likely to depend on existing `mir-semantics` support for raw-pointer-heavy `MaybeUninit`, `Box`, and internal-node aliasing patterns in `alloc::collections::btree`.
- Any need for non-local tooling or a snapshot refresh is a blocker until it is explicitly escalated and recorded.

## Cross-Challenge Notes

- Likely reuse candidates include prior `verify-rust-std` contracts for pointer provenance, `MaybeUninit` slice access, raw-pointer reborrows, and tree-shaped ownership transfer patterns.
- The node/handle separation in this module is a good candidate for reusing any existing harness structure that already distinguishes safe navigation from destructive ownership transitions.
- If later challenges in `alloc::collections::btree` need similar parent-link or edge-index reasoning, this branch should leave a compact invariants note that can be copied forward.

## History

- Bootstrap record created by orchestrator.
- Planner replaced the placeholder extraction fields with a challenge-specific scope contract and sprint breakdown.
