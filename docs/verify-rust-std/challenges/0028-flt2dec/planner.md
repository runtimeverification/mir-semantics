# Planner Record: Challenge 0028

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0028-flt2dec.md
- Tracking issue: [#524](https://github.com/model-checking/verify-rust-std/issues/524)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`
- Generator record: `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0028-flt2dec/evaluator.md`

## Requirements Extraction

- Published goal: verify `core::num::flt2dec`, the standard-library float-to-decimal conversion module used for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, and the dragon-strategy `format_shortest` and `format_exact`; for generic inputs, the proof may be limited to primitive types.
- Challenge-specific UB obligations: prevent dangling or misaligned loads/stores, avoid compiler-intrinsic UB, avoid mutating immutable bytes, and avoid producing invalid values.
- Additional safety conditions from source docs or SAFETY comments: calls to `assume_init()` must only occur on fully initialized values, and the lifetime-laundering pattern in this module must be shown not to create UB.

## Scope Contract

- In scope for current branch: planning artifacts only, challenge-local evidence capture, and a single narrow delegation target for the generator.
- Out of scope unless later justified: implementation in `library/*`, proof edits, backend changes, or cross-repo dependency work.
- Exceptional dependency escalation policy: if the next probe reaches the float backend gap already seen on challenge 0011, record the exact failing operation and only escalate after confirming it is a structural backend limitation rather than a wrapper artifact.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | done |
| 1 | Remove the wrapper slice-index artifact from the first probe path | One narrower `digits_to_dec_str` follow-up probe target and its rerun evidence are written down | in progress |

## Dependencies And Blockers

- Reused blocker signal from challenge 0011 remains relevant, but the first 0028 run did not reproduce it; the immediate blocker is now the wrapper's `SliceIndex::index` leaf rooted at `#applyBinOp ( binOpOffset , ... )`.
- No challenge-local artifacts beyond the probe harness and its evidence are present yet in the artifact directory.

## Cross-Challenge Notes

- Challenge 0011 provides the strongest reuse pattern: keep integer/safe-path reasoning separate from the float-sensitive path, and record the exact backend limitation instead of labeling the challenge generically blocked.
- The current challenge is narrower in name but broader in unsafe surface: it combines float formatting, `assume_init()`, and lifetime laundering, so the plan should stay anchored to one representative probe rather than the full function set.
- The first probe already targeted `digits_to_dec_str`; the next highest-leverage slice is to remove the probe wrapper's range indexing so the follow-up result can distinguish a true `flt2dec` blocker from a harness artifact.

## History

- Bootstrap record created by orchestrator.
- Reconfirmed published requirements and the earlier float blocker signal before narrowing the next generator task.
