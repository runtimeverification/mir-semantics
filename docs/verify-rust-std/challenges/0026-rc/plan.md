# Challenge 0026 Plan

## Objective

Turn the published `Rc`/`Weak` challenge requirements into one concrete proof-order matrix so the generator can start from the highest-leverage API cluster instead of spreading across the whole `alloc::rc` surface.

## Confirmed Contract Surface

- Published goal: verify `Rc` and `Weak` in `alloc::rc`.
- Public unsafe APIs: 12 listed functions must have safety contracts and verified contracts.
- Internal unsafe APIs: at least 75% of the listed non-public unsafe functions must be either proven unconditionally safe or given safety contracts.
- Proof limits: primitive `T` only; allocators only from the standard library (`Global` and `System`).
- UB coverage: dangling or misaligned pointer access, compiler intrinsic UB, mutating immutable bytes, and invalid values.
- Challenge-book rules still apply: automation, PR-based workflow, approved tools, and no stdlib runtime changes unless separately justified.

## Single Next Technical Subtask

Audit the `alloc::rc` raw-pointer and refcount-transition family, map each function to its source SAFETY comment and likely proof entrypoint, and choose the smallest first tranche that gives the most leverage toward the 12 public unsafe contracts.

## Why This Comes First

These APIs define the ownership and count-transition invariants that the rest of `Rc` and `Weak` builds on. If the tranche is chosen poorly, later proof work will duplicate invariant discovery instead of reusing it.

## Exit Criteria

- A function-by-function matrix exists for the raw-pointer/refcount APIs.
- The first tranche is explicitly named.
- Any external blocker, including the public Kani dependency note from issue #382, is marked as a dependency rather than assumed.
