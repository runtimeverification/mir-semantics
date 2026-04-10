# Challenge 0011: Verification Harnesses for Numeric Primitive Methods

This directory holds the branch-local verification harnesses and
fail/frontier harnesses for
[verify-rust-std challenge 0011](https://model-checking.github.io/verify-rust-std/challenges/0011-floats-ints.html).
These files are not generic regression tests. The auditable progress map lives
in `docs/verify-rust-std/challenges/0011-floats-ints/success_criteria.md`.

## Verification harnesses

- `unchecked_add.rs`, `unchecked_sub.rs`, `unchecked_mul.rs`,
  `unchecked_shl.rs`, `unchecked_shr.rs`, and `unchecked_neg.rs` cover the
  published Part 1 unsafe integer methods.
- `wrapping_shl.rs`, `wrapping_shr.rs`, `widening_mul.rs`, and
  `carrying_mul.rs` cover the published Part 2 safe APIs.
- These harnesses are executed through the dedicated `test_verify_rust_std`
  collector and can also be replayed with direct `kmir prove-rs` calls when a
  single start symbol needs isolation.

## Fail And Frontier Harnesses

- `unchecked_add-fail.rs`, `unchecked_sub-fail.rs`, `unchecked_mul-fail.rs`,
  `unchecked_shl-fail.rs`, `unchecked_shr-fail.rs`, and
  `unchecked_neg-fail.rs` preserve branch-local fail/frontier expectations for
  the unsafe integer methods.
- `to_int_unchecked-fail.rs` is the current minimal reproducer/frontier harness
  for Part 3. It exists to keep the float blocker auditable until the backend
  can support the required float intrinsics. If Part 3 becomes provable, the
  passing harness should move to `to_int_unchecked.rs`, while this fail harness
  should remain focused on explicit frontier and UB-reproducer cases.
- Expected-output artifacts for the frontier harnesses live under `show/`.
  Important examples are:
  `show/to_int_unchecked-fail.to_int_unchecked_f32_i32.expected`,
  `show/to_int_unchecked-fail.to_int_unchecked_f64_i64.expected`, and
  `show/unchecked_shr-fail.unchecked_shr_u8.expected`.

## Run Commands

- Full local challenge replay through the dedicated collector:
  `make test-verify-rust-std PARALLEL=1 TEST_ARGS="-k '0011-floats-ints'"`
- Narrow collection check for the next technical step:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_shl and not fail" -q`
- Direct proof replay for the next technical step:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs --start-symbol unchecked_shl_u128 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shl-u128 --reload --fail-fast --max-workers 1`
- Float frontier-harness replay against the checked-in `show/*.expected`
  artifacts:
  `make test-verify-rust-std PARALLEL=1 TEST_ARGS="-k 'to_int_unchecked and fail'"`
- Parked integer-frontier replay against the checked-in `show/*.expected`
  artifacts:
  `make test-verify-rust-std PARALLEL=1 TEST_ARGS="-k 'unchecked_shr and fail'"`

## CI Discoverability

- The branch already has the dedicated `test-verify-rust-std` make target and
  the `test_verify_rust_std` pytest collector.
- `.github/workflows/test.yml` now exposes an explicit `Verify Rust Std` job
  that runs `make test-verify-rust-std PARALLEL=6`, so reviewers can see this
  collector directly in GitHub Actions instead of inferring it from the general
  integration suite.
