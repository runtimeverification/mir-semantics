# Success Criteria: Challenge 0009 Duration

## Coverage Matrix

### Constructors (5/5 covered)

| Method | Harness | Status |
|--------|---------|--------|
| `Duration::new` | new.rs | PASS |
| `Duration::from_secs` | from_secs.rs | PASS |
| `Duration::from_millis` | from_millis.rs | PASS |
| `Duration::from_micros` | from_micros.rs | PASS |
| `Duration::from_nanos` | from_nanos.rs | PASS |

### Accessors (7/7 covered)

| Method | Harness | Status |
|--------|---------|--------|
| `as_secs` | from_secs.rs, accessors.rs | PASS |
| `as_millis` | accessors.rs | PASS |
| `as_micros` | accessors.rs | PASS |
| `as_nanos` | accessors.rs | PASS |
| `subsec_millis` | from_millis.rs, accessors.rs | PASS |
| `subsec_micros` | from_micros.rs, accessors.rs | PASS |
| `subsec_nanos` | from_secs.rs, from_nanos.rs, accessors.rs | PASS |

### Arithmetic (3/4 covered)

| Method | Harness | Status | Notes |
|--------|---------|--------|-------|
| `checked_add` | checked_add.rs | PASS | Tests basic add and nanos carry |
| `checked_sub` | checked_sub.rs | PASS | Tests basic sub and nanos borrow |
| `checked_mul` | checked_mul.rs | PASS | Tests basic mul and nanos mul |
| `checked_div` | checked_div.rs | BLOCKED | `#cast(IntToInt)` unsupported |

### UB Safety

All passing proofs execute with `--terminate-on-thunk`, which halts on any
unresolved operation. The proofs verify that no undefined behavior occurs during
execution of the tested methods with the given concrete inputs.

### Fail Variants (5 total)

| Fail Harness | Verifies |
|-------------|----------|
| from_secs-fail.rs | Wrong subsec_nanos assertion detected |
| from_millis-fail.rs | Wrong as_secs assertion detected |
| new-fail.rs | Wrong as_secs assertion detected |
| accessors-fail.rs | Wrong subsec_millis assertion detected |
| checked_add-fail.rs | Wrong as_secs assertion detected |

## Summary

- **15/16 methods verified** (93.75% coverage)
- **9 passing harnesses** + **5 expected-fail harnesses** = **14 total harnesses**
- **1 blocked method** (`checked_div`) due to missing `#cast(IntToInt)` semantic rule
- All proofs complete in under 60 seconds each
