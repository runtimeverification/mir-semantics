# Evaluation Result: Challenge 0013

Independent evaluator refresh completed on the re-execution branch. The upstream
Challenge 13 bar is unchanged: implement `Invariant` for `CStr`, verify the nine
safe methods, annotate and verify contracts for `from_ptr`,
`from_bytes_with_nul_unchecked`, and `strlen`, and verify `CloneToUninit` plus
`Index<RangeFrom<usize>>`.

The branch now has the prerequisite cross-crate body-resolution slice, linked
`CStr` fixture support, and challenge-local `CStr` artifacts. The new
`c93bbe4a` edition-2024 change moved standalone prove targets past the prior
frontend issue, but the challenge still stops on concrete proof frontiers rather
than closed Challenge 13 evidence.

## Verdict

`IN PROGRESS`

## Score

`2.0`

## Satisfied Criteria

- Dedicated branch and worktree exist, and the evaluation trail is isolated on
  `verify-rust-std/reexec-0013-cstr`.
- The branch now contains direct prerequisite evidence for cross-crate
  body-resolution on `kmir/cstr.smir.json`.
- The branch now contains challenge-local `CStr` artifacts:
  `from_ptr.rs` with `test_from_ptr` and `test_index_range_from_exact_bytes`,
  `from_bytes_with_nul_unchecked.rs` with
  `test_from_bytes_with_nul_unchecked_ok`, and
  `clone_to_uninit.rs` with `test_clone_to_uninit_exact_bytes`.
- The new exact-byte `CloneToUninit` harness is destination-validity aware: it
  uses an initialized destination buffer, an explicit `len <= dest.len()` guard,
  and compares the exact written region against `cstr.to_bytes_with_nul()`.
- `generator.md` and `workpad.md` record reproducible commands and outcomes,
  including the edition-2024 rerun on `c93bbe4a`.
- The branch now shows two distinct proof frontiers instead of a single
  bootstrap failure: the linked-SMIR path still stops at
  `core::ffi::CStr::from_bytes_with_nul`, and the standalone exact-byte
  `CloneToUninit` target now reaches a separate `#decodeConstant` thunk on the
  `c"hello"` literal.

## Missing Criteria

- The nine safe-method invariant checks are absent.
- `from_bytes_with_nul_unchecked` still needs proof discharge, and `strlen`
  remains missing.
- The current `Index<RangeFrom<usize>>` artifact exists, but its proof still
  fails and needs refinement before it can count as discharge evidence.
- No completed challenge-local proof result exists for the full published
  `CStr` requirements.

## Blocking Issues

- This is not a hard blocker. The prerequisite port and edition-2024 compile
  fix are useful, but the branch still has unresolved proof frontiers rather
  than completed Challenge 13 evidence.
- The linked-SMIR `test_clone_to_uninit` path is still blocked by the concrete
  missing-body/stuck frontier at `core::ffi::CStr::from_bytes_with_nul`.
- The standalone exact-byte `CloneToUninit` slice now fails earlier on a local
  `#decodeConstant` thunk for `c"hello"` at
  `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs:19`,
  so it is not yet a closed proof either.

## Evidence

- Challenge 13 requirements were reconfirmed from the upstream verify-rust-std
  challenge page:
  - `Invariant` for `CStr`
  - nine safe methods
  - unsafe contracts for `from_ptr`, `from_bytes_with_nul_unchecked`, and
    `strlen`
  - `CloneToUninit` and `Index<RangeFrom<usize>>`
- Branch head includes prerequisite port commit `80244466`, evidence commit
  `d0517441`, and edition-2024 compile fix commit `c93bbe4a`.
- `generator.md` records a successful `resolve_bodies`-style check, a linked
  proof run on `test_from_ptr`, and failing challenge-local proofs for
  `test_from_ptr`, `test_index_range_from_exact_bytes`, and
  `test_from_bytes_with_nul_unchecked_ok`.
- Fresh reruns on `c93bbe4a` show:
  - `kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit`
    still fails with a stuck leaf at
    `core::ffi::c_str::CStr::from_bytes_with_nul`
  - `kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk`
    now fails on a `#decodeConstant` thunk instead of the older frontend issue
- `workpad.md` records the remaining gap: missing `from_bytes_with_nul_unchecked`
  and `strlen` artifacts, plus the shared
  `core::ffi::CStr::from_bytes_with_nul` frontier on the linked-SMIR path.

## Next Action Required To Improve State

- Reduce the linked-SMIR `core::ffi::CStr::from_bytes_with_nul` frontier so the
  shared constructor body is available to the `CloneToUninit` path.
- Eliminate or isolate the standalone exact-byte harness's `c"hello"`
  `#decodeConstant` thunk so that proof path can exercise the same CStr
  constructor body instead of stopping at local constant decoding.
- Then continue the remaining Challenge 13 work: the nine safe-method invariant
  checks, `from_ptr`, `from_bytes_with_nul_unchecked`, `strlen`, and the
  `Index<RangeFrom<usize>>` proof.
