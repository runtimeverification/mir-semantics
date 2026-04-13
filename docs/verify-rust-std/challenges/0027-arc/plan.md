---
challenge: "0027-arc"
status: in_progress
priority: p0
iteration: 1
last_updated: 2026-04-11
---

## Requirements

**Goal:** Verify the unsafe `Arc` / `Weak` implementation surface in `alloc::sync`.

**Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0027-arc.md  
**Tracking issue:** [#383](https://github.com/model-checking/verify-rust-std/issues/383)

### Challenge obligations

- Verify the public unsafe `Arc` / `Weak` APIs with explicit safety contracts.
- Cover the raw-pointer recovery and refcounting family first, because that is the currently selected branch slice.
- Keep proof harnesses symbolic and keep concrete frontier reproducers separate.
- Respect the challenge-specific UB obligations called out in the branch material:
  dangling or misaligned pointer access, invalid values, intrinsic UB, immutable-byte mutation, and data-race hazards.

### Current branch-local scope

- First target: `Arc<T, A>::from_raw_in`.
- Follow-on targets after the root proof stabilizes:
  `Arc::increment_strong_count_in`, `Arc::decrement_strong_count_in`, `Weak::from_raw_in`, and thin `Global` wrappers.
- Deferred for later tranches:
  `assume_init`, `get_mut_unchecked`, `downcast_unchecked`, and broader helper coverage outside the raw-pointer/refcount spine.

## Success Criteria Matrix

### Proof status snapshot (2026-04-11)

| Harness | Role | Status | Frontier / Result | Notes |
| --- | --- | --- | --- | --- |
| `arc-from-raw-in.rs` | symbolic verification harness | PASS | closed | Root contract proof for `Arc::from_raw_in` is available on this branch |
| `arc-from-raw-in-frontier-fail.rs` | concrete frontier reproducer | EXPECTED-FAIL | `failing: 1`, `stuck: 1` | Keep as the minimal reproducer for the remaining unresolved path |

### Coverage map

| Requirement slice | Current Status | Harness / Artifact | Next requirement |
| --- | --- | --- | --- |
| `Arc<T, A>::from_raw_in` root proof | VERIFIED | `arc-from-raw-in.rs` | Preserve pass while shrinking or explaining the remaining frontier repro |
| Shared raw-pointer helper frontier | BLOCKED | `arc-from-raw-in-frontier-fail.rs` | Determine whether the `malloc` `noBody` path is a missing body, allocator modeling gap, or a wrapper setup issue |
| `Arc::increment_strong_count_in` / `decrement_strong_count_in` | NOT STARTED | none yet | Reuse the proven root proof shape once the shared frontier is understood |
| `Weak::from_raw_in` | NOT STARTED | none yet | Reuse raw-recovery spine after Arc-side frontier is stable |
| Thin `Global` wrappers | NOT STARTED | none yet | Queue after allocator-generic roots are stable |

## Sprint Plan

### Sprint 0: Lock in the root proof

- Keep `arc-from-raw-in.rs` green.
- Treat the passing harness as the baseline contract shape for the raw-pointer tranche.

### Sprint 1: Triage the remaining frontier

- Re-run `arc-from-raw-in-frontier-fail.rs` and inspect the `failing: 1` plus `stuck: 1` leaves.
- Confirm whether the current node-3 `malloc` `noBody` site is the same shared blocker family seen in related raw-pointer challenges.
- Do not widen the reproducer; keep it concrete and minimal.

### Sprint 2: Decide blocker ownership

- If the frontier is a missing external body/model, record that as an explicit semantic dependency.
- If the frontier is local to wrapper setup or transmute/layout plumbing, extract a smaller reproducer or implement the minimal fix.
- Keep the symbolic proof harness unchanged unless the contract itself needs refinement.

### Sprint 3: Expand the raw-pointer tranche

- Add or replay `increment_strong_count_in`, `decrement_strong_count_in`, and `Weak::from_raw_in` only after the shared frontier has a stable diagnosis.
- Queue thin `Global` wrappers after allocator-generic proofs are understood.

## Blockers

| Blocker | Type | Affects | Status | Notes |
| --- | --- | --- | --- | --- |
| `malloc` `noBody` setup leaf | Semantic / modeling | `arc-from-raw-in-frontier-fail.rs` | active | Current known frontier at node 3 from the branch README |
| Shared raw-pointer helper uncertainty | Cross-challenge diagnosis | future Arc / Weak follow-ons | active | Needs comparison with the analogous `Rc`-family blocker before widening |
| Data-race obligations not yet encoded | Specification gap | later `Arc` tranche | pending | Not a blocker for the current root proof, but must be explicit before claiming broader challenge coverage |
