# Evaluation Result: Challenge 0013

Independent evaluator refresh completed on the re-execution branch. The branch
has now landed a prerequisite cross-crate body-resolution slice, a linked CStr
fixture, and multiple challenge-local `CStr` artifacts, including a new exact-
byte `CloneToUninit` harness. The harness is still blocked by a shared
`core::ffi::CStr::from_bytes_with_nul` frontier, so the full published `CStr`
set remains incomplete.

## Verdict

`IN PROGRESS`

## Score

`2.0`

## Satisfied Criteria

- Dedicated branch, worktree, and draft PR exist.
- The branch now contains direct prerequisite evidence for cross-crate body
  resolution on `kmir/cstr.smir.json`.
- The branch now contains challenge-local `CStr` artifacts:
  `from_ptr.rs` with `test_from_ptr` and `test_index_range_from_exact_bytes`,
  plus `from_bytes_with_nul_unchecked.rs` with
  `test_from_bytes_with_nul_unchecked_ok`, plus
  `clone_to_uninit.rs` with `test_clone_to_uninit_exact_bytes`.
- `generator.md` and `workpad.md` record reproducible commands and outcomes,
  including proof failures that expose branch-local frontiers for `from_ptr`,
  `Index<RangeFrom<usize>>`, `from_bytes_with_nul_unchecked`, and the new
  exact-byte `CloneToUninit` slice.
- The rubric now distinguishes prerequisite linker work, exact-byte evidence,
  and actual Challenge 13 completion evidence.
- The new `CloneToUninit` harness is destination-validity aware: it uses an
  initialized destination buffer, an explicit `len <= dest.len()` guard, and
  compares the exact written region against `cstr.to_bytes_with_nul()`.

## Missing Criteria

- The nine safe-method invariant checks are absent.
- `from_bytes_with_nul_unchecked` still needs proof discharge, and `strlen`
  remains missing.
- `CloneToUninit` has exact-byte harness evidence, but the proof still stalls at
  `core::ffi::CStr::from_bytes_with_nul`.
- The current `Index<RangeFrom<usize>>` artifact exists, but its proof fails
  and still needs refinement before it can count as discharge evidence.
- No completed challenge-local proof result exists for the full published
  `CStr` requirements.

## Blocking Issues

- This is not a hard blocker. The prerequisite port is useful, and the branch
  now has challenge-local artifacts, but the current proofs still fail on
  branch-local frontiers.
- The new exact-byte `CloneToUninit` slice reaches a precise missing-body/stuck
  frontier at `core::ffi::CStr::from_bytes_with_nul`, which is actionable but
  still prevents meaningful discharge for that slice.

## Evidence

- Branch head includes prerequisite port commit `80244466` and evidence commit
  `d0517441`, plus challenge-artifact commits `5cd0bae4`, `91e6317f`, and
  `89f2a5e6`.
- `generator.md` records a successful `resolve_bodies`-style check, a linked
  proof run on `test_from_ptr`, and failing challenge-local proofs for
  `test_from_ptr`, `test_index_range_from_exact_bytes`, and
  `test_from_bytes_with_nul_unchecked_ok`.
- `workpad.md` records the remaining gap: missing `from_bytes_with_nul_unchecked`
  and `strlen` artifacts, plus the shared `core::ffi::CStr::from_bytes_with_nul`
  frontier now blocking the exact-byte `CloneToUninit` slice.

## Next Action Required To Improve State

- Implement the actual Challenge 13 `CStr` artifacts:
  - invariant harnesses for the nine safe APIs
  - contracts and proof harnesses for `from_ptr`,
    `from_bytes_with_nul_unchecked`, and `strlen`
  - discharge the exact-byte `CloneToUninit` slice and refine
    `Index<RangeFrom<usize>>`
- Re-run the narrowest scoped validation on the resulting challenge-local
  artifacts and reduce the failing `from_ptr` / index /
  `from_bytes_with_nul_unchecked` / `CloneToUninit` frontiers to proven or
  explicitly blocked states.
