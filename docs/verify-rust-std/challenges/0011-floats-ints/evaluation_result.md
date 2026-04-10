# Evaluation Result: Challenge 0011

## Verdict

`IN PROGRESS`

## Score

`2.98 / 3`

## Strict Scorecard

| Criterion | Score | Rationale |
| --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 3 | The branch maps the challenge families to `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/` harnesses, the `show/*.expected` float frontier, and the challenge docs. |
| Challenge-book rules are satisfied | 3 | Work remains challenge-local, reviewable, and automation-backed; no stdlib runtime logic was modified. |
| Safety conditions are modeled faithfully | 3 | The float and integer obligations are separated, and the float blocker is tied to specific stuck intrinsics rather than a vague unsupported-floats claim. |
| Undefined behavior obligations are covered | 2 | The non-float proof matrix is expanding, but the full set of integer widths and all float obligations are not yet proven. |
| Evidence is reproducible | 3 | The exact `pytest --collect-only` and `kmir prove-rs` commands are recorded in `generator.md` and `workpad.md`. |
| Scope is challenge-local and cherry-pickable | 3 | The evidence comes from a single challenge branch with narrow doc-only refreshes and scoped proof runs. |
| Review feedback patterns are incorporated | 2 | The branch keeps each proof slice narrow and records explicit next actions, but there is no substantive review-feedback cycle to incorporate beyond conservative evaluator framing. |
| Residual risk is explicit | 3 | The remaining float-capability blocker and the still-broad integer matrix gap are both called out directly. |
| Integer methods have branch-local proof evidence | 2 | `unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`, `unchecked_mul_u32`, `unchecked_mul_u64`, `unchecked_shl_u8`, `unchecked_shl_u16`, `unchecked_shl_u32`, and `unchecked_shl_u64` pass, but the integer matrix is still incomplete. |
| Non-float APIs are mapped to concrete artifacts | 3 | The published non-float method families are represented by direct harnesses and expected-output artifacts on the branch. |
| Float path is classified with direct evidence | 3 | `to_int_unchecked-fail.*.expected` shows stuck `fabsf32` / `fabsf64` frontiers. |
| Validation is replayable | 3 | The evaluator can replay the branch-local reads and proof runs from the recorded commands and artifact paths. |

## Satisfied Criteria

- Dedicated branch, worktree, and draft PR exist.
- Challenge-local planner, generator, and workpad artifacts exist and were
  updated on the challenge branch.
- The published challenge scope is mapped to concrete artifacts in
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/`,
  including the non-float method harnesses and the float
  `to_int_unchecked-fail` harness.
- Reproducible commands and their outcomes are recorded in `generator.md`
  and `workpad.md`.
- Fifteen direct proof slices now complete end-to-end on the branch:
  `unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`,
  `unchecked_mul_u32`, `unchecked_mul_u64`, `unchecked_shl_u8`,
  `unchecked_shl_u16`, `unchecked_shl_u32`, and
  `unchecked_shl_u64` all
  passed with `ProofStatus.PASSED`.
- The branch now has branch-local proof evidence across nine Part 1
  arithmetic slices and six Part 2 safe-API slices, which is materially
  stronger than the prior evaluation but still short of broad matrix coverage.
- The float path is classified with direct branch-local evidence: the
  `to_int_unchecked-fail.*.expected` files show stuck `fabsf32` and `fabsf64`
  intrinsics for the `f32` and `f64` cases.

## Missing Criteria

- The published Part 1 matrix is still incomplete at the proof level: the
  branch has only a narrow set of passed slices, and the remaining integer-type
  combinations are still unproven, including the `unchecked_shr` family.
- Part 2 remains only partially covered because the branch has only one passed
  slice each for the wrapping-shift families, `widening_mul`, and
  `carrying_mul`, while the remaining integer-type combinations are still
  unproven.
- Part 3 remains unproven for the challenge as a whole; the branch-local
  blocker still affects `to_int_unchecked` for at least `f32` and `f64`, and
  the remaining float cases are still not proven.
- No terminal verdict stronger than `IN PROGRESS` is justified while that
  breadth gap remains open, because the remaining integer/safe-API surface is
  still broad rather than narrowly external.

## Blocking Issues

- The float path still has a precise backend blocker in the current stack:
  `to_int_unchecked-fail.to_int_unchecked_f32_i32.expected` and
  `to_int_unchecked-fail.to_int_unchecked_f64_i64.expected` stop at stuck
  `fabsf32` / `fabsf64` intrinsics.
- The remaining integer and safe-API surface is still broad enough to make
  meaningful forward progress; this is a gap, not a terminal blocker.

## Evidence

- The latest proof-pass commit is `fe0bafed17621a59c88528d449bad92b06227fdc`
  (`docs: checkpoint unchecked_shl_u64`).
- The latest plan update is `8abba7dc` (`docs(verify-rust-std): retarget 0011
  to unchecked_mul_u64`), which moves the next generator target to
  `unchecked_mul_u64`.
- `generator.md` records the completed proof runs for
  `unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`,
  `unchecked_mul_u32`, `unchecked_mul_u64`, `unchecked_shl_u8`,
  `unchecked_shl_u16`, `unchecked_shl_u32`, and `unchecked_shl_u64`,
  including the exact `kmir prove-rs` commands.
- `workpad.md` records the same fifteen passing slices and keeps the float blocker
  separate from the integer proof work.
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/README.md`
  lists the published non-float APIs and the float harness set.
- The float frontier is shown directly in:
  - `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/to_int_unchecked-fail.to_int_unchecked_f32_i32.expected`
  - `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/to_int_unchecked-fail.to_int_unchecked_f64_i64.expected`
  - `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/to_int_unchecked-fail.to_int_unchecked_f16_i8.expected`
  - `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/to_int_unchecked-fail.to_int_unchecked_f128_i128.expected`

## Next Action Required To Improve State

- Attack the float frontier directly by reducing the `to_int_unchecked`
  failure to the precise `fabsf32` / `fabsf64` stuck intrinsic path, then rerun
  the narrow float harnesses from the challenge branch and reassess whether the
  remaining work is still blocked by backend capability rather than by
  challenge-local proof coverage.
