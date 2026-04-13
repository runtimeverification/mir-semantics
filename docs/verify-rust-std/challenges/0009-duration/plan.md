---
challenge: "0009-duration"
status: evaluating
priority: p0
iteration: 1
last_updated: 2026-04-11
---

## Challenge Requirements

**Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0009-duration.md
**Tracking Issue:** [#72](https://github.com/model-checking/verify-rust-std/issues/72) (CLOSED)

### Goal

Write function contracts for `core::time::Duration` that can be used as safe abstractions.
Many `Duration` methods are safe abstractions over unsafe code (e.g., `Duration::new` uses
`unsafe { Nanoseconds(nanos) }` after validating that `nanos < NANOS_PER_SEC`).

### Required Functions (16 total)

**Constructors (5):**
1. `Duration::new(secs: u64, nanos: u32) -> Duration`
2. `Duration::from_secs(secs: u64) -> Duration`
3. `Duration::from_millis(millis: u64) -> Duration`
4. `Duration::from_micros(micros: u64) -> Duration`
5. `Duration::from_nanos(nanos: u64) -> Duration`

**Accessors (7):**
6. `Duration::as_secs(&self) -> u64`
7. `Duration::as_millis(&self) -> u128`
8. `Duration::as_micros(&self) -> u128`
9. `Duration::as_nanos(&self) -> u128`
10. `Duration::subsec_millis(&self) -> u32`
11. `Duration::subsec_micros(&self) -> u32`
12. `Duration::subsec_nanos(&self) -> u32`

**Arithmetic (4):**
13. `Duration::checked_add(&self, rhs: Duration) -> Option<Duration>`
14. `Duration::checked_sub(&self, rhs: Duration) -> Option<Duration>`
15. `Duration::checked_mul(&self, rhs: u32) -> Option<Duration>`
16. `Duration::checked_div(&self, rhs: u32) -> Option<Duration>`

### UB Obligations

All proofs must ensure absence of:
- Accessing a place that is dangling or based on a misaligned pointer
- Reading from uninitialized memory
- Mutating immutable bytes
- Producing an invalid value

All SAFETY comments in the Duration source code must be respected (nanos field must be < 1_000_000_000).

## Success Criteria Matrix

| # | Method/Property | Harness | Status | Proof Result | Blocker |
|---|---|---|---|---|---|
| 1 | `Duration::new` | new.rs | PASS | ProofStatus.PASSED | -- |
| 2 | `Duration::from_secs` | from_secs.rs | PASS | ProofStatus.PASSED | -- |
| 3 | `Duration::from_millis` | from_millis.rs | PASS | ProofStatus.PASSED | -- |
| 4 | `Duration::from_micros` | from_micros.rs | PASS | ProofStatus.PASSED | -- |
| 5 | `Duration::from_nanos` | from_nanos.rs | PASS | ProofStatus.PASSED | -- |
| 6 | `as_secs` | from_secs.rs, from_millis.rs, accessors.rs | PASS | ProofStatus.PASSED | -- |
| 7 | `as_millis` | accessors.rs | PASS | ProofStatus.PASSED | -- |
| 8 | `as_micros` | accessors.rs | PASS | ProofStatus.PASSED | -- |
| 9 | `as_nanos` | accessors.rs | PASS | ProofStatus.PASSED | -- |
| 10 | `subsec_millis` | from_millis.rs, accessors.rs | PASS | ProofStatus.PASSED | -- |
| 11 | `subsec_micros` | from_micros.rs, accessors.rs | PASS | ProofStatus.PASSED | -- |
| 12 | `subsec_nanos` | from_secs.rs, from_nanos.rs, new.rs, accessors.rs | PASS | ProofStatus.PASSED | -- |
| 13 | `checked_add` (Some path) | checked_add.rs | PASS | ProofStatus.PASSED | -- |
| 14 | `checked_sub` (Some path) | checked_sub.rs | PASS | ProofStatus.PASSED | -- |
| 15 | `checked_mul` (Some path) | checked_mul.rs | PASS | ProofStatus.PASSED | -- |
| 16 | `checked_div` (Some path) | checked_div.rs | PASS | ProofStatus.PASSED | -- |
| 13b | `checked_add` (None/overflow) | checked_add_overflow.rs | BLOCKED | ProofStatus.FAILED (1 failing) | Niche-encoded Option decoding |
| 14b | `checked_sub` (None/underflow) | checked_sub_underflow.rs | BLOCKED | ProofStatus.FAILED (1 failing) | Niche-encoded Option decoding |
| 15b | `checked_mul` (None/overflow) | checked_mul_overflow.rs | BLOCKED | ProofStatus.FAILED (1 failing) | Niche-encoded Option decoding |
| 16b | `checked_div` (None/div-by-zero) | checked_div_zero.rs | BLOCKED | ProofStatus.FAILED (1 failing) | Niche-encoded Option decoding |
| -- | Fail variant: from_secs | from_secs-fail.rs | EXPECTED FAIL | ProofStatus.FAILED (1 failing, 1 stuck) | -- |
| -- | Fail variant: from_millis | from_millis-fail.rs | EXPECTED FAIL | ProofStatus.FAILED (1 failing, 1 stuck) | -- |
| -- | Fail variant: new | new-fail.rs | EXPECTED FAIL | ProofStatus.FAILED (1 failing, 1 stuck) | -- |
| -- | Fail variant: accessors | accessors-fail.rs | EXPECTED FAIL | ProofStatus.FAILED (1 failing, 1 stuck) | -- |
| -- | Fail variant: checked_add | checked_add-fail.rs | EXPECTED FAIL | ProofStatus.FAILED (1 failing, 1 stuck) | -- |

**Summary:** 16/16 required methods have passing proofs (Some/happy path). 4 overflow/underflow None-path harnesses are blocked by niche encoding. 5 fail variants confirm proof soundness.

## Semantic Changes Applied

Two changes in `kmir/src/kmir/kdist/mir-semantics/rt/data.md` (commit `4e709123`):

### 1. operandMove fix (`#readProjection(true)` -> `#readProjection(false)`)

**Before:** `operandMove` invalidated the source local by writing `Moved` back, causing failures when the Rust compiler reuses a local via multiple `operandMove` instructions on Copy types.

**After:** `operandMove` behaves like `operandCopy` -- reads the value without invalidating the source. This is correct because:
- The Rust compiler generates `operandMove` for Copy types (integers, booleans)
- The borrow checker guarantees no use-after-move at the type level
- Aligns with Miri's behavior
- Only processes compiler-validated MIR

**Impact:** Unblocked `checked_div` (previously stuck on `#cast(Moved, castKindIntToInt, ...)` when the MIR reused a Cast-type local via `operandMove`).

### 2. `#cast(Moved, _, _, _) => Moved` rule

Safety-net rule that propagates `Moved` through cast operations. Theoretically unnecessary under the new semantics (since `operandMove` no longer produces `Moved` values), but harmless as defense-in-depth.

**Scope concern:** These are cross-cutting semantic changes affecting all KMIR proofs, not just challenge 0009. Should ideally be reviewed as a standalone PR.

## Sprint Plan

- [x] Sprint 0: Bootstrap challenge understanding, extract requirements
- [x] Sprint 1: Constructors (5 harnesses) + Accessors (1 combined harness) -- 11 proofs pass
- [x] Sprint 2: Arithmetic (add/sub/mul) -- 3 proofs pass + 5 fail variants
- [x] Sprint 3: Fix operandMove to unblock checked_div, add overflow/underflow harnesses
- [ ] Sprint 4: Resolve niche-encoded `Option<Duration>` decoding for None-path verification
- [ ] Sprint 5: Split operandMove semantic fix into standalone PR for cherry-pickability

## Blockers & Dependencies

### Active Blockers

1. **Niche-encoded `Option<Duration>` decoding** (mir-semantics gap)
   - **Impact:** All 4 overflow/underflow harnesses fail with `UnableToDecode(bytes, typeInfoEnumType(...Option<Duration>...))`
   - **Root cause:** KMIR's constant decoding does not implement niche-based discriminant resolution. The `None` variant uses `nanos >= 1_000_000_000` as niche (layout: `tagEncodingNiche` with `wrappingRange(start: 0, end: 1000000000)`)
   - **Not** a stable-mir-json gap -- the layout information is correctly extracted
   - **Status:** No fix PR exists. Needs to be filed as a tracked issue.

### Resolved Blockers

1. ~~`checked_div` blocked by `#cast(IntToInt)` unsupported~~ -- **RESOLVED** in Sprint 3 via operandMove fix
2. ~~`Option<Duration>` niche encoding for `.unwrap()` path~~ -- **WORKAROUND:** Use `.unwrap()` for Some cases, `.is_none()` for None cases

### Scope / Cherry-pickability Concern

The `operandMove` fix in `rt/data.md` is a cross-cutting K semantics change. For clean cherry-picking:
- Challenge harnesses and test wiring should be in one PR
- The operandMove semantic fix should be a separate standalone PR

## Reproducibility

All proofs verified on 2026-04-11 using:
```bash
# From the repository root (or challenge worktree):
uv --project kmir run -- kmir prove <file> \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0009-plan-<name> --reload --fail-fast
```

Each proof takes ~60-90s (dominated by LLVM kompile step) and the proof itself completes in 0s.

## Cross-Challenge Notes

- The `operandMove` fix benefits any challenge whose MIR uses `operandMove` on Copy-type locals that are referenced multiple times (common pattern in Rust MIR for integer operations).
- The niche-encoded `Option` decoding blocker will also affect any challenge that verifies `None` return paths from methods returning `Option<T>` where `T` has a niche.
- Test wiring pattern (`test_integration.py` discovery + exclusion list) is reusable for other VRS challenges.

## Files

### Harnesses (19 total)
All in `kmir/src/tests/integration/data/verify-rust-std/0009-duration/`:
- `new.rs`, `from_secs.rs`, `from_millis.rs`, `from_micros.rs`, `from_nanos.rs`
- `accessors.rs`
- `checked_add.rs`, `checked_sub.rs`, `checked_mul.rs`, `checked_div.rs`
- `checked_add_overflow.rs`, `checked_sub_underflow.rs`, `checked_mul_overflow.rs`, `checked_div_zero.rs`
- `from_secs-fail.rs`, `from_millis-fail.rs`, `new-fail.rs`, `accessors-fail.rs`, `checked_add-fail.rs`

### Semantic Changes
- `kmir/src/kmir/kdist/mir-semantics/rt/data.md` (operandMove fix + #cast Moved rule)

### Test Wiring
- `kmir/src/tests/integration/test_integration.py` (test_vrs_0009_duration)
