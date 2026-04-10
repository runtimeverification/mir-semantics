# Workpad: Challenge 0029

## 2026-04-10 Harness Sweep Pass 1

- Reconfirmed the upstream challenge page and copied the full success surface
  into `success-criteria.md`.
- Selected the first root tranche to maximize breadth:
  raw ownership recovery (`from_raw*`, `from_non_null*`) plus initialization
  conversion (`assume_init` scalar and slice).
- Chose direct raw-allocation witnesses for the first harnesses so they hit the
  target boxed APIs directly instead of getting blocked inside higher-level
  constructors such as `Box::new_in`.
- Existing public branch-local evidence before this pass:
  `kmir/src/tests/integration/data/prove-rs/box_heap_alloc-fail.rs` already
  showed a transmute frontier on a generic `Box::new` path, so this sweep tries
  to separate root boxed API entrypoints from generic constructor noise.

## Evidence To Refresh After Validation

- Compile validation completed with `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen` for:
  - `box-from-raw.rs`
  - `box-from-raw-in.rs`
  - `box-from-non-null.rs`
  - `box-from-non-null-in.rs`
  - `box-assume-init.rs`
  - `box-slice-assume-init.rs`
- Narrow proof commands executed:
  - `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw.rs --start-symbol verify_box_from_raw --proof-dir /tmp/boxed-from-raw-proof --verbose --terminate-on-thunk`
  - `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw-in.rs --start-symbol verify_box_from_raw_in --proof-dir /tmp/boxed-from-raw-in-proof --verbose --terminate-on-thunk`
- First concrete frontier:
  both proofs fail at the same `thunk(#cast(Integer(4,64,false), castKindTransmute, ...))`
  leaf in `std::alloc::Layout::new::<u32>`; see:
  - `/tmp/boxed-from-raw-proof/box-from-raw.verify_box_from_raw/proof.json`
  - `/tmp/boxed-from-raw-in-proof/box-from-raw-in.verify_box_from_raw_in/proof.json`
  - `kmir show ... --nodes 4 --full-printer` output recorded during this pass
- The blocker is provisionally challenge-external and classified as
  `MIR_SEMANTICS`, since it reproduces before the boxed API body-specific
  postconditions are reached.
