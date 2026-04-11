# Evaluator Record: Challenge 0009

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0009-duration.md
- Tracking issue: [#72](https://github.com/model-checking/verify-rust-std/issues/72)
- Planner record: `docs/verify-rust-std/challenges/0009-duration/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0009-duration/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0009-duration/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Coverage Verification

### Required Functions (16 total)

All 16 required functions have corresponding harness files:

| # | Function | Harness(es) | Status |
|---|----------|-------------|--------|
| 1 | `Duration::new` | new.rs | PASS |
| 2 | `Duration::from_secs` | from_secs.rs | PASS |
| 3 | `Duration::from_millis` | from_millis.rs | PASS |
| 4 | `Duration::from_micros` | from_micros.rs | PASS |
| 5 | `Duration::from_nanos` | from_nanos.rs | PASS |
| 6 | `as_secs` | from_secs.rs, from_millis.rs, accessors.rs | PASS |
| 7 | `as_millis` | accessors.rs | PASS |
| 8 | `as_micros` | accessors.rs | PASS |
| 9 | `as_nanos` | accessors.rs | PASS |
| 10 | `subsec_millis` | from_millis.rs, accessors.rs | PASS |
| 11 | `subsec_micros` | from_micros.rs, accessors.rs | PASS |
| 12 | `subsec_nanos` | from_secs.rs, from_nanos.rs, new.rs, accessors.rs | PASS |
| 13 | `checked_add` | checked_add.rs | PASS |
| 14 | `checked_sub` | checked_sub.rs | PASS |
| 15 | `checked_mul` | checked_mul.rs | PASS |
| 16 | `checked_div` | checked_div.rs | PASS (unblocked in sprint 2) |

Coverage: **16/16 PASS = 100%**

### Fail Variants (5 total)

| Fail Harness | Verifies | Status |
|-------------|----------|--------|
| from_secs-fail.rs | Wrong `subsec_nanos` assertion (claims 1, should be 0) | EXPECTED FAIL |
| from_millis-fail.rs | Wrong `as_secs` assertion (claims 2, should be 1) | EXPECTED FAIL |
| new-fail.rs | Wrong `as_secs` assertion (claims 6, should be 5) | EXPECTED FAIL |
| accessors-fail.rs | Wrong `subsec_millis` assertion (claims 600, should be 500) | EXPECTED FAIL |
| checked_add-fail.rs | Wrong `as_secs` assertion (claims 7, should be 8) | EXPECTED FAIL |

### Overflow/Underflow Harnesses (4 total, all BLOCKED)

| Harness | Tests | Status | Blocker |
|---------|-------|--------|---------|
| checked_add_overflow.rs | MAX + 1s/1ns -> None | BLOCKED | niche-encoded `Option<Duration>` decoding |
| checked_sub_underflow.rs | 3s - 5s -> None, 0 - 1ns -> None | BLOCKED | niche-encoded `Option<Duration>` decoding |
| checked_mul_overflow.rs | MAX * 2 -> None | BLOCKED | niche-encoded `Option<Duration>` decoding |
| checked_div_zero.rs | 15s / 0 -> None | BLOCKED | niche-encoded `Option<Duration>` decoding |

## Harness Correctness Review

All harnesses reviewed for semantic correctness:

1. **from_secs.rs** - Tests roundtrip with 0, 1, 42. Verifies `as_secs()` returns input and `subsec_nanos()` is 0. Correct per Duration spec.
2. **from_millis.rs** - Tests with 0, 1000, 1500, 2999. Verifies seconds/millis decomposition (e.g., 1500ms = 1s + 500ms). Correct.
3. **from_micros.rs** - Tests with 0, 1M, 1.5M, 2999999. Verifies seconds/micros decomposition. Correct.
4. **from_nanos.rs** - Tests with 0, 1B, 1.5B, 2999999999. Verifies seconds/nanos decomposition. Correct.
5. **new.rs** - Tests constructor with carry behavior (nanos >= 1B carries to seconds). Tests 6 cases including overflow carry. Thorough and correct.
6. **accessors.rs** - Tests all 6 accessor variants on `Duration::new(5, 500_000_000)`. All expected values mathematically verified. Correct.
7. **checked_add.rs** - Tests basic add (5s + 3s = 8s) and nanos carry (1.5s + 2.7s = 4.2s). Carry logic verified: 500M + 700M = 1.2B nanos, 1s carry, 200M remaining. Correct.
8. **checked_sub.rs** - Tests basic sub (5s - 3s = 2s) and nanos borrow (5.2s - 2.7s = 2.5s). Borrow logic verified: 200M - 700M requires borrowing 1s. Correct.
9. **checked_mul.rs** - Tests basic mul (5s * 3 = 15s) and nanos mul (1.5s * 2 = 3.0s). Correct.
10. **checked_div.rs** - Tests simple division (15s / 3 = 5s). Harness is correct and now passes.
11. **checked_add_overflow.rs** - Correct harness: MAX Duration + 1s/1ns should return None. Blocked by niche decoding.
12. **checked_sub_underflow.rs** - Correct harness: 3s - 5s and 0 - 1ns should return None. Blocked by niche decoding.
13. **checked_mul_overflow.rs** - Correct harness: MAX * 2 should return None. Blocked by niche decoding.
14. **checked_div_zero.rs** - Correct harness: 15s / 0 should return None. Blocked by niche decoding.

All assertions are semantically meaningful, non-trivially true, and aligned with Rust Duration documentation.

**Weakness noted**: The overflow/underflow None-branch is tested in 4 harnesses, but all 4 are BLOCKED by niche encoding. This means the `None` return path of arithmetic operations is unverified. The harnesses exist and are correct, but cannot pass until KMIR supports niche-encoded enum decoding. The 10 passing arithmetic/constructor harnesses only exercise the `Some(...)` path via `.unwrap()`.

## operandMove Semantic Fix Analysis (Sprint 2 Critical Review)

### Change Summary

Two changes in `rt/data.md`:

1. **`operandMove` now uses `#readProjection(false)` instead of `#readProjection(true)`** -- This makes `operandMove` behave identically to `operandCopy`: it reads the value without writing `Moved` back to the source local.

2. **`#cast(Moved, _, _, _) => Moved` rule added** -- A safety-net rule that propagates `Moved` through cast operations rather than getting stuck.

### Evaluation of Correctness

**The `operandMove` change is semantically defensible for well-typed Rust programs.** Here is the reasoning:

- In Rust MIR, `operandMove` is used by the compiler even for Copy types (integers, booleans, structs containing only Copy fields). The Rust borrow checker guarantees no use-after-move at the type level, so the compiler freely generates `operandMove` for locals that are read multiple times.
- KMIR only processes compiler-validated MIR (output of `rustc`), so use-after-move on non-Copy types is impossible in valid input.
- This aligns with Miri's behavior: Miri does not invalidate locals on move for the same reason.
- The original `Moved` sentinel was a defense-in-depth mechanism. Removing it is safe for well-typed programs but reduces KMIR's ability to detect malformed MIR (not a concern for this use case).

**Specific scenario that was fixed**: In `Duration::checked_div`, the MIR uses `operandMove` on a Copy-type local (integer) that is subsequently used again in a cast expression. Under the old semantics: (1) first `operandMove` reads the value and writes `Moved`; (2) second access via `rvalueCast` evaluates `operandMove` which now reads `Moved`; (3) `#cast(Moved, castKindIntToInt, ...)` gets stuck. Under the new semantics, the local is never invalidated, so the second access succeeds.

**The `#cast(Moved, _, _, _) => Moved` rule assessment**: This rule is theoretically unnecessary under the new semantics (since `operandMove` no longer produces `Moved` values). However:
- It is harmless and acts as a safety net
- Its documentation comment is misleading -- it describes a scenario that should not occur under the new semantics. Minor documentation issue, not a correctness concern.

**Risk assessment**: LOW. The change is correct for all valid Rust MIR. The only downside is loss of defense-in-depth for detecting malformed MIR, which is not a realistic attack vector for this verification challenge. The change is consistent with how Miri and other MIR interpreters handle moves.

### Scope Concern

This change modifies `kmir/src/kmir/kdist/mir-semantics/rt/data.md`, which is a **cross-cutting semantics file** affecting all KMIR proofs, not just challenge 0009. The change is semantically sound, but:
- It should be reviewed as a standalone mir-semantics PR, not bundled with challenge-specific harnesses
- It may affect other challenges or the existing test suite
- CI integration tests (currently IN_PROGRESS on PR #1034) will be the definitive check

## Niche Encoding Blocker Classification

**Category: mir-semantics gap**

The `UnableToDecode` error occurs in KMIR's constant decoding pipeline when it encounters bytes that represent a niche-encoded `Option<Duration>` in the `None` variant. The layout shows `tagEncodingNiche` with the tag field using `wrappingRange(start: 0, end: 1000000000)` -- meaning the niche is `nanos >= 1_000_000_000`.

This is NOT a stable-mir-json gap (the layout information including niche encoding details is correctly extracted). It IS a mir-semantics gap -- KMIR's byte-to-value decoding does not implement niche-based discriminant resolution.

**Impact**: All 4 overflow/underflow harnesses are blocked. The `None` return path of `checked_add`, `checked_sub`, `checked_mul`, and `checked_div` is unverified.

**Per evaluation protocol**: Gaps require fix PRs, not documentation. No niche encoding fix PR exists.

## Reproducibility Evidence

### Evaluator Re-run Results -- Sprint 2 (independent proof dirs)

Command template:
```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0009-duration/
timeout 900 uv --project kmir run -- kmir prove kmir/src/tests/integration/data/verify-rust-std/0009-duration/<file>.rs \
  --verbose --terminate-on-thunk --proof-dir /tmp/kmir-0009-eval2-<name> --reload --fail-fast
```

| Proof | Result | Proof Dir | Notes |
|-------|--------|-----------|-------|
| checked_div.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval2-checked-div` | **NEW**: Unblocked by operandMove fix. Reproduced. |
| from_secs.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval2-from-secs` | Regression check: still passes |
| accessors.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval2-accessors` | Regression check: still passes |
| checked_add.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval2-checked-add` | Regression check: still passes |
| checked_sub.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval2-checked-sub` | Regression check: still passes |
| checked_mul.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval2-checked-mul` | Regression check: still passes |
| checked_add_overflow.rs | FAILED (4 nodes, 1 failing) | `/tmp/kmir-0009-eval2-checked-add-overflow` | Blocked: UnableToDecode on niche-encoded Option<Duration> |
| from_secs-fail.rs | FAILED (3 nodes, 1 failing, 1 stuck) | `/tmp/kmir-0009-eval2-from-secs-fail` | Expected failure reproduced |

8 proofs reproduced independently, all matching expected outcomes.

## Test Integration Wiring

The test suite in `test_integration.py` (lines 118-138) correctly:
- Discovers all `.rs` files in the `0009-duration` directory
- Explicitly excludes the 4 niche-blocked harnesses: `checked_add_overflow`, `checked_sub_underflow`, `checked_mul_overflow`, `checked_div_zero`
- Includes `checked_div` (no longer excluded after the fix)
- Routes `*-fail.rs` files to `assert apr_proof.failed`
- Routes other files to `assert apr_proof.passed`
- Uses `--terminate-on-thunk` via `ProveOpts`

## CI Status (PR #1034)

As of evaluation time:
- Code Quality Checks: SUCCESS
- Unit Tests: SUCCESS
- Integration with stable-mir-json: SUCCESS
- Nix Tests (normal): SUCCESS
- Nix Tests (MacM1): SUCCESS
- Integration Tests (LLVM, Haskell, Proofs, etc.): IN_PROGRESS

No failures observed. Full CI results pending for integration tests.

## Scorecard

| Criterion | Critical | Score | Evidence | Gap |
|-----------|----------|-------|----------|-----|
| Published success criteria mapped to artifacts | yes | 3 | All 16 functions have harness files. All 16 PASS. `checked_div` unblocked by operandMove fix. | None (all 16/16 pass) |
| Challenge-book rules satisfied | yes | 3 | Automated, reviewable, no runtime logic changes to std library | None |
| Safety conditions modeled faithfully | yes | 2 | All 16 passing proofs run with `--terminate-on-thunk`. Concrete inputs cover representative cases including carry/borrow. | Overflow/underflow None-branch unverified (4 harnesses blocked by niche encoding). Only `Some(...)` path tested for arithmetic ops. |
| UB obligations covered | yes | 2 | `--terminate-on-thunk` catches unresolved operations. All 16 proofs complete without thunks. No invalid values, no uninitialized reads in exercised paths. | `None` return paths of arithmetic ops unverified due to niche encoding gap |
| Evidence reproducible | yes | 3 | 8 proofs reproduced independently with correct outcomes (6 PASS, 1 BLOCKED, 1 EXPECTED FAIL) | None |
| Scope is challenge-local and cherry-pickable | yes | 2 | Harnesses and test wiring are challenge-local. However, the `operandMove` fix in `rt/data.md` is a cross-cutting semantic change affecting all KMIR proofs. | Semantic fix should ideally be a separate PR from challenge harnesses |
| Review feedback patterns incorporated | no | 2 | Fail variants provided; test wiring follows existing patterns; overflow harnesses added per sprint 1 evaluator feedback | No prior external review patterns to incorporate |
| Residual risk explicit | no | 3 | Niche encoding blocker precisely documented with root cause. operandMove fix scope documented. CI status tracked. | None |

## Verdict

**IN_PROGRESS**

### Rationale

The challenge has made significant progress in Sprint 2. The `checked_div` blocker is resolved, achieving 16/16 function coverage. However, the submission cannot be marked SUBMISSION_READY because:

1. **Overflow/underflow None-branch testing is blocked by niche encoding** (mir-semantics gap). Four harnesses exist but all fail with `UnableToDecode` on niche-encoded `Option<Duration>`. The `None` return paths of `checked_add`, `checked_sub`, `checked_mul`, and `checked_div` are unverified. Per evaluation protocol, gaps need fix PRs. No niche encoding fix PR exists.

2. **Safety conditions score is 2/3** (critical criterion must be 3). The arithmetic operations only verify the `Some(...)` happy path. The overflow/underflow edge cases -- which are the primary safety concern for `checked_*` operations -- are completely untested due to the niche encoding gap. For a verification challenge focused on safety, this is a significant gap.

3. **Scope cherry-pickability is 2/3** (critical criterion must be 3). The `operandMove` fix in `rt/data.md` is a cross-cutting K semantics change that affects ALL KMIR proofs. It should be submitted as a separate mir-semantics PR (with its own test coverage) rather than bundled with challenge-0009 harnesses. This makes the PR non-trivially cherry-pickable.

4. **CI integration tests still IN_PROGRESS** at evaluation time. Cannot confirm the `operandMove` change does not cause regressions in existing proofs.

### Actionable Critique for Next Generator Sprint

1. **Priority 1: Split the operandMove fix into a standalone PR**. The semantic change in `rt/data.md` should be submitted independently from the challenge harnesses. This makes the challenge PR cherry-pickable and allows the semantic fix to get independent review.

2. **Priority 2: File a niche encoding issue/PR** for mir-semantics. The `UnableToDecode` for niche-encoded enums is a known gap that blocks verification of `None`-returning paths. Even if the fix takes time, filing a tracked issue is necessary.

3. **Priority 3: Once niche encoding is supported**, re-run the 4 overflow/underflow harnesses (`checked_add_overflow.rs`, `checked_sub_underflow.rs`, `checked_mul_overflow.rs`, `checked_div_zero.rs`) and confirm they pass.

4. **Minor: Fix the misleading comment** on `#cast(Moved, _, _, _) => Moved`. The comment says "after an operandMove on a Copy-type local that was used again" but this scenario no longer occurs under the new semantics.

### What Improved Since Sprint 1

- `checked_div` is now PASSING (was BLOCKED) -- the primary Sprint 1 blocker is resolved
- 4 new overflow/underflow harnesses exist (were missing) -- addresses Sprint 1 Priority 2 feedback
- Coverage is now 16/16 functions (was 15/16) -- all required functions exercised

### What Remains

- Niche encoding support in mir-semantics (blocks overflow/underflow verification)
- PR decomposition (semantic fix vs. challenge harnesses)
- CI completion confirmation

## Iteration Log

- Bootstrap record created by orchestrator.
- 2026-04-11: First evaluator assessment completed. Reproduced 5 proofs (3 PASS, 1 BLOCKED, 1 EXPECTED FAIL). Classified `checked_div` blocker as mir-semantics gap. Verdict: IN_PROGRESS.
- 2026-04-11: Second evaluator assessment (Sprint 2). Reproduced 8 proofs (6 PASS, 1 BLOCKED, 1 EXPECTED FAIL). Confirmed `checked_div` now passes after operandMove fix. Reviewed operandMove semantic change -- assessed as correct but cross-cutting. Classified niche encoding as mir-semantics gap. CI partially complete (no failures). Verdict: IN_PROGRESS.
