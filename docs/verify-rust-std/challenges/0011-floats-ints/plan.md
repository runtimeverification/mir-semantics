# Execution Plan: Challenge 0011

Current objective:
- Tighten Challenge 11 into an auditable verification portfolio by adding a
  persistent success-criteria map, clarifying which files are passing
  verification harnesses versus fail/frontier harnesses, and keeping the next
  technical proof step fixed on `unchecked_shl_u128`.

Next generator task:
- When technical proof work resumes, prove `unchecked_shl_u128` end-to-end
  with a scoped `kmir prove-rs` run on
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs`
  using `--start-symbol unchecked_shl_u128`, then record whether the branch
  extends the already-passing `unchecked_shl` family beyond
  `unchecked_shl_u64` without reopening the exhausted `unchecked_shr`
  diagnostic path.

Generator acceptance evidence:
- `docs/verify-rust-std/challenges/0011-floats-ints/success_criteria.md`
  maps every published function family to a branch-local harness or an
  explicit blocker.
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/README.md`
  distinguishes passing verification harnesses from fail/frontier harnesses
  and records exact replay commands.
- The challenge docs reference the same artifact structure and preserve
  `unchecked_shl_u128` as the next technical step.

Plan slices:
1. Derive a persistent requirement table directly from the challenge page.
2. Align the harness README and evaluator-facing docs around that table.
3. Keep the next technical move on `unchecked_shl_u128`; leave
   `unchecked_shr` parked and keep the float blocker explicit.

Stop conditions:
- Stop after the artifact-structure refresh lands; this checkpoint does not
  perform new semantic fixing.
- Do not reopen `unchecked_shr` until there is evidence stronger than the
  current shared `binOpShrUnchecked` frontier.
- Do not widen scope into float/backend work in this checkpoint; the next
  technical proving step remains `unchecked_shl_u128`.
