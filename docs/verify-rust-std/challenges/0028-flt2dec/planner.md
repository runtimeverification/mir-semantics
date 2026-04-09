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
- Exceptional dependency escalation policy: if the next probe reproduces the float backend gap already seen on challenge 0011, record the exact failing operation and only escalate after confirming it is a structural backend limitation rather than a missing artifact.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | done |
| 1 | Isolate the first float-capable probe | One minimal challenge-local probe target and its rerun evidence are written down | pending |

## Dependencies And Blockers

- Reused blocker signal from challenge 0011: the float path previously stalled on missing KMIR / haskell-backend float-value support, so the first delegation should test whether 0028 hits the same backend boundary before any broader decomposition.
- No challenge-local artifacts beyond the bootstrap README are present yet in the artifact directory.

## Cross-Challenge Notes

- Challenge 0011 provides the strongest reuse pattern: keep integer/safe-path reasoning separate from the float-sensitive path, and record the exact backend limitation instead of labeling the challenge generically blocked.
- The current challenge is narrower in name but broader in unsafe surface: it combines float formatting, `assume_init()`, and lifetime laundering, so the plan should stay anchored to one representative probe rather than the full function set.
- The first probe should target `digits_to_dec_str`, since it is the simplest named top-level safe entry point in the published success criteria.

## History

- Bootstrap record created by orchestrator.
- Reconfirmed published requirements and the earlier float blocker signal before narrowing the next generator task.
