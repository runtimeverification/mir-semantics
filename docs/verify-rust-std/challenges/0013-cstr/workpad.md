# Challenge 0013 Workpad

## Handoff State

- Branch: `verify-rust-std/reexec-0013-cstr`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr`
- Current stage: planner-only bootstrap refinement
- Implementation status: not started

## Evidence Gathered

- Upstream challenge page for Challenge 13 defines the target as `CStr`
  safety/invariant verification plus contracts for the unsafe entry points.
- Public solution PRs `model-checking/verify-rust-std#543` and `#566` both
  show the final challenge shape: invariant harness, nine safe methods, three
  unsafe contracts, `CloneToUninit`, and `Index<RangeFrom<usize>>`.
- Review comments on `#543` and `#566` identify the main quality trap:
  `CloneToUninit` must be proven against the exact writable region and not via
  an oversized helper buffer or a harness that could go undefined on bugged
  implementations.
- The local reference branch `verify-rust-std/challenge-0013-0028` is a useful
  context source for CStr-related linker/body-resolution behavior, but it is
  not currently the primary path for this challenge.

## Decisions

- Keep the first generator slice focused on `CStr` verification artifacts rather
  than widening scope into unrelated std changes.
- Treat the `CloneToUninit` contract as the highest-risk technical point in the
  challenge.
- Prefer exact, reviewer-readable evidence in the eventual evaluator record:
  file paths, commands, and byte-level assertions.

## Failed Attempts

- None. This is still the initial planning pass.

## Next Handoff

- Generator should implement the challenge-local harness and contract slice
  described in `plan.md`.
- Evaluator should add rubric criteria that distinguish exact-byte evidence from
  merely "a passing harness".
