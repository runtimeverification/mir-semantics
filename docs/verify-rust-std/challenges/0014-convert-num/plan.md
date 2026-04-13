---
challenge: "0014-convert-num"
status: in_progress
priority: p1
iteration: 1
last_updated: 2026-04-11
---

## Requirements

**Goal:** Verify the safety of primitive numeric conversions in `core::convert::num`.

**Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0014-convert-num.md  
**Tracking issue:** [#220](https://github.com/model-checking/verify-rust-std/issues/220)

### Branch-local scope from the README

- `nonzero_from.rs` covers representative widening `NonZero` conversions.
- `nonzero_try_from.rs` covers representative fallible narrowing `NonZero` conversions.
- `to_int_unchecked.rs` covers representative float-to-int `to_int_unchecked` conversions.
- Keep proof harnesses replayable and separate from any future minimal frontier reproducers.
- Keep semantic changes and proof/harness changes organized so they can be cherry-picked cleanly.

### Current verification posture

- The branch already has 3 harness files, but the latest reported sweep produced no usable proof output.
- For planning purposes, treat all three harnesses as **attempted but unevaluated** until replay determines whether they errored before proof construction, timed out, or stopped at a stable frontier.
- The first objective is therefore evidence recovery, not scope expansion.

## Success Criteria Matrix

### Proof status snapshot (2026-04-11)

| Harness | Scope | Current Status | Evidence | Next requirement |
| --- | --- | --- | --- | --- |
| `nonzero_from.rs` | widening `NonZero` conversions (`u8 -> u16`, `i8 -> i16`) | NO PROOF OUTPUT | Latest sweep produced neither pass/fail proof evidence nor a recorded frontier | Re-run one representative start symbol and capture the first concrete outcome |
| `nonzero_try_from.rs` | fallible narrowing `NonZero` conversions (`u16 -> u8`, `i16 -> i8`, cross-sign cases) | NO PROOF OUTPUT | Same as above | Determine whether the first blocker is branching/overflow logic, decoding, or infra |
| `to_int_unchecked.rs` | float-to-int `to_int_unchecked` family (`f16`, `f32`, `f64`, `f128`) | NO PROOF OUTPUT | Same as above | Determine whether float support, intrinsic support, or timeout is the limiting factor |

### Coverage map

| Requirement slice | Representative harness | Status | Notes |
| --- | --- | --- | --- |
| `NonZero` invariant preservation during widening conversions | `nonzero_from.rs` | HARNESS READY, UNASSESSED | Harness exists; no current proof result is recorded |
| Fallible narrowing conversions preserve `NonZero` safety and result shape | `nonzero_try_from.rs` | HARNESS READY, UNASSESSED | Includes same-sign and cross-sign witnesses |
| `to_int_unchecked` safety under documented finite/in-range preconditions | `to_int_unchecked.rs` | HARNESS READY, UNASSESSED | Likely highest semantic risk because it mixes float semantics with conversion preconditions |

**Exit condition for this matrix:** replace each `NO PROOF OUTPUT` row with `PASSED`, `FAILED`, `STUCK`, `TIMEOUT`, or `ERROR`, together with the first concrete frontier or blocker family.

## Sprint Plan

### Sprint 0: Recover evidence

- Re-run one representative start symbol from each harness using the branch README replay commands.
- Classify each run as `error`, `timeout`, `failed`, `stuck`, or `passed`.
- If a harness fails before proof construction, record the exact failing tool stage instead of treating it as a semantic frontier.

### Sprint 1: Stabilize the first frontier

- Pick the cheapest nontrivial harness with reproducible output.
- If the blocker is semantic, shrink to a dedicated reproducer without polluting the proof harness.
- If the blocker is infra or timeout, reduce proof depth or pick a smaller start symbol to recover a stable first leaf.

### Sprint 2: Convert harness presence into auditable coverage

- For `nonzero_from.rs`, discharge or precisely block one signed and one unsigned widening case.
- For `nonzero_try_from.rs`, discharge or precisely block one same-sign and one cross-sign narrowing case.
- For `to_int_unchecked.rs`, discharge or precisely block one float family representative with explicit precondition handling.

### Sprint 3: Expand within the existing harness set

- Fill in the remaining start symbols already present in the three harnesses before adding new files.
- Only add challenge-local reproducers after a stable frontier is identified.

## Blockers

| Blocker | Type | Affects | Status | Notes |
| --- | --- | --- | --- | --- |
| Missing proof output from latest sweep | Evidence gap | all three harnesses | active | Could be timeout, tool failure, or missing proof persistence |
| Unknown first semantic frontier | Semantic triage | all three harnesses | active | No leaf or failing rule has been recorded yet |
| Potential float/intrinsic gaps | Semantics | `to_int_unchecked.rs` | suspected | Needs replay evidence before escalation |

