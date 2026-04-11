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
| 16 | `checked_div` | checked_div.rs | BLOCKED (mir-semantics gap) |

Coverage: 15/16 PASS, 1/16 BLOCKED = 93.75%

### Fail Variants (5 total)

| Fail Harness | Verifies | Status |
|-------------|----------|--------|
| from_secs-fail.rs | Wrong `subsec_nanos` assertion (claims 1, should be 0) | EXPECTED FAIL |
| from_millis-fail.rs | Wrong `as_secs` assertion (claims 2, should be 1) | EXPECTED FAIL |
| new-fail.rs | Wrong `as_secs` assertion (claims 6, should be 5) | EXPECTED FAIL |
| accessors-fail.rs | Wrong `subsec_millis` assertion (claims 600, should be 500) | EXPECTED FAIL |
| checked_add-fail.rs | Wrong `as_secs` assertion (claims 7, should be 8) | EXPECTED FAIL |

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
10. **checked_div.rs** - Tests simple division (15s / 3 = 5s). Harness is correct but blocked on semantics gap.

All assertions are semantically meaningful, non-trivially true, and aligned with Rust Duration documentation.

**Weakness noted**: Overflow/underflow edge cases (e.g., `checked_add` with values that overflow to `None`, `checked_sub` resulting in `None`) are NOT tested because of the `Option<Duration>` niche decoding limitation (documented in generator.md under Blockers). The `.is_none()` workaround mentioned is not implemented in any harness. This means the `None` branch of arithmetic operations is unverified.

## Reproducibility Evidence

### Evaluator Re-run Results (independent proof dirs)

Command template:
```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0009-duration/
timeout 900 uv --project kmir run -- kmir prove kmir/src/tests/integration/data/verify-rust-std/0009-duration/<file>.rs \
  --verbose --terminate-on-thunk --proof-dir /tmp/kmir-0009-eval-<name> --reload --fail-fast
```

| Proof | Result | Proof Dir | Notes |
|-------|--------|-----------|-------|
| from_secs.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval-from-secs` | Reproduced |
| accessors.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval-accessors` | Reproduced |
| checked_add.rs | PASSED (3 nodes, 0 failing, 0 stuck) | `/tmp/kmir-0009-eval-checked-add` | Reproduced |
| checked_div.rs | FAILED (4 nodes, 1 failing, 0 stuck) | `/tmp/kmir-0009-eval-checked-div` | Reproduced (thunk on cast) |
| from_secs-fail.rs | FAILED (3 nodes, 1 failing, 1 stuck) | `/tmp/kmir-0009-eval-from-secs-fail` | Reproduced (expected) |

## checked_div Failure Analysis

### Frontier Inspection

```
Node 3 (step 91): #cast(Moved, castKindIntToInt, ty(27), ty(25))
  function: std::time::Duration::checked_div
  span: /rust/library/core/src/time.rs:822

Node 4 (leaf, terminal): thunk(#cast(Moved, castKindIntToInt, ty(27), ty(25)))
```

### Root Cause Classification

**Category: (a) mir-semantics gap**

The `#cast` rules in `kmir/src/kmir/kdist/mir-semantics/rt/data.md` (lines 1384-1412) only match on `Integer(...)` or `BoolVal(...)` as the first argument. When the value at the cast site is `Moved` (a sentinel indicating the variable's value has been moved out), no rule fires and execution thunks.

The `Moved` value reaching the cast operation indicates that the operand resolution phase before the cast does not properly reconstruct the actual value from memory in this code path. This requires a fix in the mir-semantics operational rules -- either:
- Adding a rule to resolve `Moved` values before casting, or
- Fixing the operand loading sequence so `Moved` is replaced with the actual value before the cast is attempted

**Impact**: Until this mir-semantics gap is fixed with a PR, `checked_div` cannot pass. This is NOT an issue in Duration's implementation nor a spec violation -- it is a tooling limitation.

## Test Integration Wiring

The test suite in `test_integration.py` (line 118-138) correctly:
- Discovers all `.rs` files in the `0009-duration` directory
- Explicitly excludes `checked_div` from the test matrix (line 119)
- Routes `*-fail.rs` files to `assert apr_proof.failed`
- Routes other files to `assert apr_proof.passed`
- Uses `--terminate-on-thunk` via `ProveOpts`

## Scorecard

| Criterion | Critical | Score | Evidence | Gap |
|-----------|----------|-------|----------|-----|
| Published success criteria mapped to artifacts | yes | 2 | All 16 functions have harness files. 15/16 PASS. 1/16 BLOCKED. | `checked_div` blocked by mir-semantics gap; no fix PR exists |
| Challenge-book rules satisfied | yes | 3 | Automated, reviewable, no runtime logic changes | None |
| Safety conditions modeled faithfully | yes | 2 | All passing proofs run with `--terminate-on-thunk`. Concrete inputs cover representative cases including carry/borrow. | No overflow-to-None edge cases tested; `Option<Duration>` niche decoding workaround documented but not implemented |
| UB obligations covered | yes | 2 | `--terminate-on-thunk` catches unresolved operations. All 15 passing proofs complete without thunks. | `checked_div` UB path unverified due to tooling gap |
| Evidence reproducible | yes | 3 | All 5 sampled proofs reproduced independently with correct outcomes | None |
| Scope is challenge-local and cherry-pickable | yes | 3 | Changes confined to `0009-duration/` data dir and test_integration.py | None |
| Review feedback patterns incorporated | no | 2 | Fail variants provided; test wiring follows existing patterns | No prior review patterns to incorporate |
| Residual risk explicit | no | 3 | `checked_div` blocker precisely documented with root cause. `Option<Duration>` niche decoding limitation documented. | None |

## Verdict

**IN_PROGRESS**

### Rationale

The challenge cannot be marked SUBMISSION_READY because:

1. **`checked_div` is BLOCKED by a mir-semantics gap** (`#cast(Moved, castKindIntToInt, ...)` has no matching rule). This is category (a) -- mir-semantics gap -- which per the evaluation rules means the verdict CANNOT be SUBMISSION_READY until a fix PR exists. No fix PR has been created.

2. **Overflow/underflow None-branch testing is missing** for arithmetic operations. The `Option<Duration>` niche decoding workaround (using `.is_none()`) is documented but not implemented in any harness. The `checked_add`, `checked_sub`, and `checked_mul` proofs only test `Some(...)` cases via `.unwrap()`.

### Actionable Critique for Next Generator Sprint

1. **Priority 1: Create a mir-semantics fix PR** for the `#cast(Moved, castKindIntToInt, ...)` gap. Specifically, add handling in `rt/data.md` to resolve `Moved` operands before cast, or fix the operand resolution sequence so the actual value is available at cast time. Once the fix PR lands, re-run `checked_div.rs` to confirm it passes.

2. **Priority 2: Add None-branch harnesses** for `checked_add`, `checked_sub`, `checked_mul` (and `checked_div` once unblocked). Example pattern:
   ```rust
   let max = Duration::new(u64::MAX, 999_999_999);
   assert!(max.checked_add(Duration::from_nanos(1)).is_none());
   ```
   If `Option<Duration>` niche decoding blocks `.is_none()`, document the attempt and thunk output as evidence.

3. **Priority 3: Add edge case coverage** -- zero-division for `checked_div` (should return `None`), multiplication by 0, subtraction resulting in exactly zero.

## Iteration Log

- Bootstrap record created by orchestrator.
- 2026-04-11: First evaluator assessment completed. Reproduced 5 proofs (3 PASS, 1 BLOCKED, 1 EXPECTED FAIL). Classified `checked_div` blocker as mir-semantics gap. Verdict: IN_PROGRESS.
