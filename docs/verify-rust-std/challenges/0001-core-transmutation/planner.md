# Planner Record: Challenge 0001

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0001-core-transmutation.md
- Tracking issue: [#19](https://github.com/model-checking/verify-rust-std/issues/19)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation`
- Generator record: `docs/verify-rust-std/challenges/0001-core-transmutation/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0001-core-transmutation/evaluator.md`

## Requirements Extraction

- Published goal: confirm the soundness of value transmutations performed by `libcore`, including public methods exposed by `libcore`. A transmutation is sound when the source value is a bit-valid instance of the destination type and when the destination type's library safety invariants are not violated by later use of the transmuted value. Safe contexts should be discharged by local reasoning; unsafe contexts may push the obligation to the caller.
- Published success criteria: add a new specification-book entry that explains the relevant transmute-verification patterns, and annotate at least 35 of the 47 listed intrinsics/functions with contracts; for non-intrinsics, their bodies must also be verified. For safe functions, preconditions and postconditions around the transmutation site are sufficient if they keep the safety argument intact.
- Challenge-specific UB obligations: prove or otherwise cover the bit-validity of each source value for the destination type, the preservation of destination invariants after the reinterpretation, and the caller-side safety preconditions for unsafe APIs that cannot be discharged locally. The challenge also expects the verification story to distinguish between direct `transmute`/`transmute_unchecked` use and later safe wrappers that rely on them.
- Additional safety conditions from source docs or SAFETY comments: do not verify the excluded categories listed in the challenge page unless they are needed to justify an in-scope function; do not rely on provenance validation work; and treat any added `Transmutability` impls as upstream dependencies that must land in Rust before this challenge can be counted as complete.
- Challenge-specific assumptions: byte-level reasoning is acceptable, but full memory-model validation is not required; `Transmutability` may be used if it helps, but only within the limits described by the challenge page; unit tests embedded in `libcore` are not required to be verified; and the omitted classes of APIs remain out of scope unless they are needed to support an in-scope proof chain.

## Scope Contract

- In scope for current branch: document the published goal into a reusable planning record, keep the scope centered on `mir-semantics`' existing integration-test and spec-book surfaces, and use the challenge-local README only if it helps keep the checklist aligned with this plan. The first implementation pass should target a small number of representative transmutation families before widening coverage.
- Out of scope unless later justified: code changes, proofs, harnesses, expected outputs, evaluator/rubric edits, generator edits, and any upstream Rust or solver/tooling changes. The excluded challenge categories stay out of scope unless a later proof path cannot be closed without them and the blocker is explicitly recorded here first.
- Exceptional dependency escalation policy: if a target function requires a new semantic hook, a new lemma, a new `Transmutability` impl, or support for an otherwise-excluded API family, record it as a blocker with the exact function group and dependency chain before any implementation work starts. Do not silently widen scope to reach the success threshold.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Establish the transmutation surface map and confirm which listed APIs are direct candidates, wrappers, or blockers | Requirements, assumptions, blockers, and reuse candidates are recorded in this planner | pending |
| 1 | Shape the core contract story for `transmute` and `transmute_unchecked` plus the minimal byte-validity/invariant obligations they imply | A narrow contract outline exists for the primitive transmutation path and the remaining APIs are grouped by reuse pattern | pending |
| 2 | Group the direct helper families that mainly forward into the primitive path, especially `MaybeUninit`, array, char/ascii, and layout/alignment-style helpers | Each family has a planned proof bundle or a documented blocker with a concrete reason | pending |
| 3 | Group the safe wrapper and adapter APIs whose proof story depends on the earlier helper families, including slice/iterator/buffer adapters and `core::str` wrappers | The plan reaches the 35-function target on paper, with any remaining gaps tied to explicit dependencies | pending |
| 4 | Consolidate the plan into the spec-book entry and the artifact checklist that generator/evaluator work can consume | The planner is stable enough for generator and evaluator baselines to start from without re-scoping | pending |

## Dependencies And Blockers

- `mir-semantics` currently lacks the actual proof artifacts for this challenge surface, so the planner has to assume the first executable work will expose which APIs are already covered by existing semantics and which ones still need support.
- The challenge explicitly excludes several transmute-adjacent families, which means the planner must not count them toward the 35-function threshold unless they become strictly necessary to verify an in-scope target.
- Any need for array, slice, pointer, or provenance-heavy reasoning is a likely blocker because the challenge page narrows the acceptable assumptions and the local feature checklist still marks those areas as unsupported or partial.
- If a proof path depends on upstream Rust acceptance of new `Transmutability` impls, that is a hard external dependency, not an internal implementation task.
- The `mir-semantics` integration surface will likely need reusable contract templates and regression harness organization before the broad safe-wrapper sweep can proceed cleanly.

## Cross-Challenge Notes

- Reuse candidate: the challenge 0011 docs and harness layout show a clean split between unsafe primitives, safe wrappers, and fail/pass evidence; that structure is a useful template for organizing transmutation families without copying its content.
- Reuse candidate: the challenge 0002 contract framing for unsafe intrinsics is a good style reference for caller obligations, especially when a safe wrapper delegates to an unsafe core operation.
- Reuse candidate: `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/README.md` and its expected-output files show how to keep challenge-local checklist entries and proof evidence aligned with a challenge-specific data directory.
- Reuse candidate: simplification-lemma work in `kmir/src/kmir/kdist/mir-semantics/lemmas/kmir-lemmas.md` is a likely pattern for any byte-mask or size-mask identities that show up while modeling transmutation-related arithmetic.

## History

- Bootstrap record created by orchestrator.
- Planner refined with published goal, success criteria, assumption boundaries, likely blockers, and a staged `mir-semantics` scope contract.
