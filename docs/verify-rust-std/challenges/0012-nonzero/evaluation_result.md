# Evaluation Result: Challenge 0012-nonzero

## Verdict

`CONDITIONALLY_SUBMISSION_READY` -- 33/36 harnesses PASS, covering 33/37 Part 2 function targets under the current grouped accounting. All implementable functions are verified. The remaining delta is entirely due to fundamental semantic gaps: pointer-to-pointer cast support (`from_mut`, `from_mut_unchecked`), `FnOnce::call_once` dispatch (`min_max`, `clamp`), and the signed `i8::MIN` edge in `wrapping_neg`.

## Score

`4.5 / 5` overall readiness

## Strict Scorecard

| Criterion | Score | Rationale |
| --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 5 | 36 harness files exist under `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/`, and the current run status is explicitly tracked for each remaining blocker family. |
| Challenge-book rules are satisfied | 4 | Work remains challenge-local and reviewable. No stdlib runtime logic was modified; the proof effort stays in harnesses and MIR semantics support. |
| Safety conditions are modeled faithfully | 4 | Construction, arithmetic, bitwise, byte-order, power-of-two, and signed-operation paths are covered. The residual safety gap is concentrated in pointer casts, `FnOnce` dispatch, and the signed minimum edge. |
| Undefined behavior obligations are covered | 4 | 33 harnesses pass, exercising the implementable UB surface for this challenge. The remaining UB obligations collapse to three known semantic infrastructure gaps rather than missing challenge-local harnesses. |
| Evidence is reproducible | 4 | Proofs are run with `kmir prove FILE --verbose --terminate-on-thunk --reload --fail-fast` and recorded in the challenge artifacts. |
| Scope is challenge-local and cherry-pickable | 4 | The challenge branch contains the harnesses and supporting semantics needed for the current frontier. Residual blockers are upstream and reusable across challenges. |
| Residual risk is explicit | 5 | The remaining risk is narrowly scoped and named: `castKindPtrToPtr`, `FnOnce::call_once`, and the `wrapping_neg` `i8::MIN` edge. |
| Function coverage breadth | 4 | Part 2 coverage is now 33/37 under the current grouped accounting, with only four blocked target slots left and no remaining straightforward local wins. |

## Harness Results Summary

**Total harnesses:** 36  
**Passing:** 33  
**Failing:** 3

### Passing Harnesses (33/36)

- Part 1 / control: `new.rs`, `new_unchecked.rs`, `get.rs`, `const_nonzero.rs`, `transmute_wrapper_u8.rs`
- Part 2: `abs.rs`, `bitor.rs`, `bitor_u8.rs`, `byte_order.rs`, `checked_add.rs`, `checked_mul.rs`, `checked_neg.rs`, `checked_next_power_of_two.rs`, `count_ones.rs`, `from_be.rs`, `from_le.rs`, `ilog2.rs`, `isqrt.rs`, `leading_trailing_zeros.rs`, `midpoint.rs`, `neg.rs`, `overflowing_neg.rs`, `pow.rs`, `reverse_bits.rs`, `rotate_left.rs`, `rotate_right.rs`, `saturating_add.rs`, `saturating_mul.rs`, `saturating_pow.rs`, `signed_ops.rs`, `unchecked_add.rs`, `unchecked_mul.rs`, `unsigned_ops.rs`

### Failing Harnesses (3/36)

| Harness | Part | Blocker | Details |
| --- | --- | --- | --- |
| `from_mut.rs` | Part 2 | `castKindPtrToPtr` | Pointer-to-pointer cast semantics are still not implemented in K |
| `min_max.rs` | Part 2 | `FnOnce::call_once` | Trait/closure dispatch for the comparison path is still not supported |
| `wrapping_neg.rs` | Part 2 | `i8::MIN` edge | The signed minimum negation path still hits a semantic edge case |

## Coverage Snapshot

Part 2 coverage is `33 / 37` under the grouped accounting used for this challenge summary. The remaining blocked target slots are:

| Target Slot | Status | Evidence |
| --- | --- | --- |
| `from_mut` family | BLOCKED | `from_mut.rs` fails on `castKindPtrToPtr`; `from_mut_unchecked` is intentionally left uncovered because it hits the same blocker immediately |
| `min_max` | BLOCKED | `min_max.rs` fails on `FnOnce::call_once` |
| `clamp` | BLOCKED | No harness yet; it shares the same `FnOnce::call_once` blocker as `min_max` |
| `wrapping_neg` | BLOCKED | `wrapping_neg.rs` fails on the signed `i8::MIN` edge |

There are no remaining challenge-local harness or intrinsic gaps on the implementable frontier. `clamp` and `from_mut_unchecked` remain uncovered only because they would fail for already-known upstream reasons.

## Remaining Blocking Issues

| Blocker | Type | Targets Affected | Feasibility |
| --- | --- | --- | --- |
| `castKindPtrToPtr` | Cast semantics | `from_mut`, `from_mut_unchecked` | Medium -- requires pointer-to-pointer cast rules in K |
| `FnOnce::call_once` | Trait dispatch | `min_max`, `clamp` | Hard -- requires general trait-dispatch / closure-call support |
| `i8::MIN` negation edge | Signed arithmetic semantics | `wrapping_neg` | Medium -- requires closing the signed-minimum negation gap cleanly |

## Submission Readiness Assessment

### Strengths

- All currently implementable challenge targets are verified.
- Harness coverage now spans arithmetic, bitwise, byte-order, power-of-two, conversion, and signed-operation paths.
- The remaining delta is no longer a challenge-local harness backlog; it has reduced to a small set of shared semantic blockers.

### Gaps

- `from_mut` / `from_mut_unchecked` remain blocked on `castKindPtrToPtr`.
- `min_max` / `clamp` remain blocked on `FnOnce::call_once`.
- `wrapping_neg` remains blocked on the signed `i8::MIN` edge case.

### Recommendation

Treat this challenge as `CONDITIONALLY_SUBMISSION_READY` for reviewer handoff. Further progress now depends on upstream semantic work rather than additional challenge-local harness writing.

## Evidence

- **Harness directory:** `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/`
- **Plan and workpad:** `docs/verify-rust-std/challenges/0012-nonzero/plan.md`, `workpad.md`
- **Proof command:** `uv --project kmir run -- kmir prove FILE --verbose --terminate-on-thunk --proof-dir /tmp/kmir-0012-nonzero --reload --fail-fast`
- **Supporting semantics:** `kmir/src/kmir/kdist/mir-semantics/rt/data.md`, `kmir/src/kmir/kdist/mir-semantics/intrinsics.md`

## Next Action Required To Improve State

1. Implement `castKindPtrToPtr` to unblock the `from_mut` family.
2. Implement `FnOnce::call_once` support to unblock `min_max` and `clamp`.
3. Resolve the signed `i8::MIN` negation edge to make `wrapping_neg` pass.
