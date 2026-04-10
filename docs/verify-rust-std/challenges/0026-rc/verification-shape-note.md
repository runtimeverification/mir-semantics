# Challenge 0026 Verification Shape Note

## Sources Compared

- `verify-rust-std` general rules in `/home/zhaoji/projs/verify-rust-std/doc/src/general-rules.md`
- Challenge 26 success criteria in `/home/zhaoji/projs/verify-rust-std/doc/src/challenges/0026-rc.md`
- Challenge 11 pattern in `/home/zhaoji/projs/verify-rust-std/doc/src/challenges/0011-floats-ints.md`
- PR #985 discussion on `runtimeverification/mir-semantics`
- Local 0011 harnesses in `kmir/src/tests/integration/data/prove-rs/`
- Current 0026 contract map and success table in `docs/verify-rust-std/challenges/0026-rc/`

## Why The Current Concrete Harness Is Not Sufficient

The current `rc-from-raw-in-frontier-fail.rs` is a concrete witness driver. It hardcodes one allocator, one witness layout, and one value path, so it only demonstrates that a specific execution reaches the current `CastKind::Transmute` frontier.

That is useful as a regression reproducer, but it is not yet verification-shaped because it does not state a reusable proof obligation for `Rc::from_raw_in`. In particular, it does not:

- expose the API under verification as a dedicated proof entrypoint
- quantify over any input space, even the limited primitive `T` space allowed by the challenge
- encode the safety preconditions as a contract boundary rather than as one hand-built witness
- separate the proof harness from the frontier reproducer

## What Verification Looks Like In This Repo

The repo already treats verification as a pair of harness styles:

- proof harnesses with symbolic inputs that prove safety under preconditions
- fail harnesses that deliberately violate preconditions and should fail or surface UB

That matches the PR #985 summary and the 0011 challenge shape. In the 0011 files, the proof target is a named function with symbolic parameters such as `check_assume(x: u64)`, while fail cases use a harness that intentionally violates the intended precondition. PR #985 also makes the distinction explicit between proof harnesses, fail harnesses, expected output, and `--terminate-on-thunk`.

For 0026, the challenge page and contract map say the verification target is the public `unsafe` API contract surface of `alloc::rc`, not one concrete execution. So `Rc::from_raw_in` should be verified as a contract-first proof target, not as a single witness trace.

## Recommended Harness Shape For `Rc::from_raw_in`

The right shape is a two-layer setup:

1. Verification harness
2. Frontier reproducer

The verification harness should be a dedicated proof entrypoint, ideally a named `#[no_mangle]` function, with:

- symbolic primitive input for the `T` value, here `u32`
- concrete `System` allocator, because the challenge limits allocators to standard-library ones
- a small helper that constructs a `repr(C)` witness with stable `MaybeUninit` plus `ptr::write`
- an explicit `addr_of!` / field-projection step that produces the raw pointer passed to `Rc::from_raw_in`
- postconditions that check the recovered `Rc` value and refcount

The frontier reproducer should stay separate and temporary. Its job is to keep the current `CastKind::Transmute` node reproducible for audit until the verification harness can be made to prove the contract directly.

## What Should Be Symbolic And What Can Stay Concrete

Symbolic:

- the primitive payload value passed into the witness helper
- the proof entrypoint itself, so the proof is attached to a named API-shaped function rather than only to `main`

Concrete:

- `System` as the allocator
- the `repr(C)` witness layout
- the raw-pointer projection from the witness into the `value` field

Safety preconditions should be represented as explicit contract boundaries around the witness helper, not as one-off value choices inside `main`. For this challenge, that means the witness should certify provenance and initialization before `Rc::from_raw_in` is called, and the proof should assert the resulting `Rc` behaves as required.

## Recommendation

Use a contract-first, two-layer harness.

- Layer 1: a verification harness for `Rc::from_raw_in`
- Layer 2: the temporary `rc-from-raw-in-frontier-fail.rs` reproducer that keeps the current frontier visible

This is the smallest shape that matches the repo rules, the 0011 precedent, and the PR #985 harness split.

## Minimal Next Implementation Step

Add a symbolic `Rc::from_raw_in` proof entrypoint that reuses the stable `MaybeUninit` witness helper and is collected as a verification harness, while keeping the existing frontier file as the separate regression reproducer.
