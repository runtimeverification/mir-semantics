# Evaluation Result: Challenge 0013

Independent evaluator refresh completed on the re-execution branch. The
published Challenge 13 bar is unchanged: implement `Invariant` for `CStr`,
verify the nine safe methods, annotate and verify contracts for `from_ptr`,
`from_bytes_with_nul_unchecked`, and `strlen`, and verify `CloneToUninit` plus
`Index<RangeFrom<usize>>`.

The branch still has the prerequisite cross-crate body-resolution slice,
linked `CStr` fixture support, and challenge-local `CStr` artifacts. The
current checkpoint on `8309b54d` shows a more precise blocker than the earlier
frontier description: donor-linked SMIR rewrites the root names before proof
setup, so `make_call_config` cannot resolve `test_clone_to_uninit` or
`test_clone_to_uninit_exact_bytes` and the donated constructor body is never
reached.

## Verdict

`BLOCKED`

## Score

`2.1`

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
- The branch now has a concrete donor-link setup blocker instead of a generic
  proof frontier: the linked-SMIR donor path can supply a constructor body, but
  proof setup fails before execution because the linked SMIR no longer exposes
  the unqualified start symbols that `make_call_config` expects.

## Missing Criteria

- The nine safe-method invariant checks are absent.
- `from_bytes_with_nul_unchecked` still needs proof discharge, and `strlen`
  remains missing.
- The current `Index<RangeFrom<usize>>` artifact exists, but its proof still
  fails and needs refinement before it can count as discharge evidence.
- No completed challenge-local proof result exists for the full published
  `CStr` requirements.

## Blocking Issues

- This is a hard, branch-local setup blocker, not a completion signal. The
  prerequisite port and edition-2024 compile fix are useful, but the donor-link
  experiment is currently the thing preventing meaningful progress on the
  highest-leverage constructor-body frontier.
- The blocker is precise and evidence-backed: donor-linked SMIR qualifies item
  names through `link()`, which drops the original unqualified roots
  `test_clone_to_uninit` and `test_clone_to_uninit_exact_bytes` before
  `make_call_config` resolves the start symbol.
- The next action is concrete and narrow: preserve or alias the original root
  item names across donor linking, or restrict qualification to the donor side
  only, then rerun the two `CloneToUninit` proof entry points.

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
  proof run on `test_from_ptr`, failing challenge-local proofs for
  `test_from_ptr`, `test_index_range_from_exact_bytes`, and
  `test_from_bytes_with_nul_unchecked_ok`, plus the exact donor-link setup
  failure.
- The branch-local checkpoint in `workpad.md` records the donor-link blocker in
  precise terms:
  - donor-linked SMIR can materialize a body-bearing synthetic item for
    `core::ffi::CStr::from_bytes_with_nul`
  - `link()` qualification rewrites the item names
  - `make_call_config` then fails with `ValueError: <start-symbol> not found in
    program`
- `workpad.md` also preserves the remaining gap: missing
  `from_bytes_with_nul_unchecked` and `strlen` artifacts, plus the
  uncompleted safe-method and trait-impl coverage.

## Next Action Required To Improve State

- Fix donor-link root-name preservation or aliasing so the proof entry points
  survive `link()` qualification and `make_call_config` can resolve the
  unqualified start symbols again.
- Once that plumbing is corrected, rerun the linked-SMIR and challenge-local
  `CloneToUninit` proofs against the donated constructor body.
- Then continue the remaining Challenge 13 work: the nine safe-method invariant
  checks, `from_ptr`, `from_bytes_with_nul_unchecked`, `strlen`, and the
  `Index<RangeFrom<usize>>` proof.
