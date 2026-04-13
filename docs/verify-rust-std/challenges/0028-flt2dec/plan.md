---
challenge: "0028-flt2dec"
status: in_progress
priority: p1
iteration: 1
last_updated: 2026-04-11
---

## Requirements

**Goal:** Verify the float-to-decimal conversion module in `core::num::flt2dec`.

**Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0028-flt2dec.md  
**Tracking issue:** [#524](https://github.com/model-checking/verify-rust-std/issues/524)

### Current branch-local scope

- Active artifact: `digits_to_dec_str_probe.rs`.
- Treat the probe as a challenge-local verification frontier, not as final coverage for the whole challenge.
- Keep the reproducer small and concrete while preserving the same post-select `digits_to_dec_str` path.
- Do not widen to the broader formatter surface until the current frontier is classified precisely.

### Published function surface currently represented in branch docs

- `digits_to_dec_str`
- `digits_to_exp_str`
- `to_shortest_str`
- `to_shortest_exp_str`
- `to_exact_exp_str`
- `to_exact_fixed_str`
- `format_shortest_opt`
- `format_shortest`
- `format_exact_opt`
- `format_exact`

## Success Criteria Matrix

### Proof status snapshot (2026-04-11)

| Harness | Scope | Status | Frontier / Result | Notes |
| --- | --- | --- | --- | --- |
| `digits_to_dec_str_probe.rs` | concrete `digits_to_dec_str` probe | FAIL | `failing: 1` | Current known frontier remains on the slice indexing path reached from the probe |

### Coverage map

| Requirement slice | Current Status | Harness / Artifact | Next requirement |
| --- | --- | --- | --- |
| `digits_to_dec_str` | FRONTIER REACHED | `digits_to_dec_str_probe.rs` | Confirm whether the failure is truly a `slice::index` semantic gap or just a reducible probe artifact |
| Remaining `flt2dec` formatting functions | NOT STARTED | `success_criteria.md` only | Leave untouched until the first `digits_to_dec_str` frontier is stable and auditable |

## Sprint Plan

### Sprint 0: Reconfirm the active frontier

- Re-run `digits_to_dec_str_probe.rs`.
- Verify that the first concrete failing leaf is still the known `Range<usize>::index` path.
- Record whether the failing path is still downstream of the copied `if exp >= buf.len()` split.

### Sprint 1: Minimize without changing the path

- Shrink only the current post-select slice-index path.
- Keep the reproducer challenge-local; do not generalize it into a library-level slice test unless the challenge-local path disappears.

### Sprint 2: Classify the blocker

- Decide whether the failure is:
  challenge-local `flt2dec` logic,
  copied control flow around decimal formatting,
  a `core::slice::index` semantic limitation,
  or a backend/modeling boundary.
- Stop shrinking once the first stable classification is obtained.

### Sprint 3: Resume challenge coverage

- If the frontier moves past `slice::index`, keep the smallest reproducer that reaches the deeper `flt2dec` logic.
- Only then start adding proof-shaped artifacts for `digits_to_dec_str` itself and the remaining formatter surface.

## Blockers

| Blocker | Type | Affects | Status | Notes |
| --- | --- | --- | --- | --- |
| `digits_to_dec_str_probe.rs` failing leaf | Semantic frontier | current probe | active | User-reported status is `failing: 1` |
| `core::slice::index` boundary | Library semantics / modeling | current probe | active | Branch README identifies this as the current exact frontier family |
| No proof-shaped harness for full `flt2dec` API surface yet | Coverage gap | remaining functions | pending | Deferred intentionally until the current frontier is stable |
