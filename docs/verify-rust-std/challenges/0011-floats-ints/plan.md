# Execution Plan: Challenge 0011

Current objective:
- Extend Challenge 11's branch-local non-float verification evidence one
  bounded slice at a time while preserving the auditable artifact structure.
- `unchecked_shl_u128` now passes end-to-end, so the next exact technical
  proof step is `unchecked_shl_i8`.

Next generator task:
- When technical proof work resumes, prove `unchecked_shl_i8` end-to-end
  with a scoped `kmir prove-rs` run on
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs`
  using `--start-symbol unchecked_shl_i8`, then record whether the branch
  extends the already-passing `unchecked_shl` family from the completed
  unsigned widths into the signed half of the published matrix without
  reopening the exhausted `unchecked_shr` diagnostic path.

Generator acceptance evidence:
- `docs/verify-rust-std/challenges/0011-floats-ints/success_criteria.md`
  maps every published function family to a branch-local harness or an
  explicit blocker.
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/README.md`
  distinguishes passing verification harnesses from fail/frontier harnesses
  and records exact replay commands.
- The challenge docs reference the same artifact structure and preserve
  `unchecked_shl_i8` as the next technical step.

Plan slices:
1. Keep the persistent requirement table and harness docs aligned with the
   current branch evidence.
2. Continue the non-float proof expansion one bounded slice at a time, next
   `unchecked_shl_i8`.
3. Leave `unchecked_shr` parked and keep the float blocker explicit.

Stop conditions:
- Stop after one bounded proof slice and the associated doc refresh land.
- Do not reopen `unchecked_shr` until there is evidence stronger than the
  current shared `binOpShrUnchecked` frontier.
- Do not widen scope into float/backend work in this checkpoint; the next
  technical proving step remains `unchecked_shl_i8`.
