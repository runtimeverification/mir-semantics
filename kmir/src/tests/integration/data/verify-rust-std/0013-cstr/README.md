# Challenge 0013: Safety of `CStr`

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0013-cstr.md
- Tracking issue: [#150](https://github.com/model-checking/verify-rust-std/issues/150)
- Current branch: `verify-rust-std/reexec-0013-cstr`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr`

Coverage and execution records:

- Success criteria coverage table: [success-criteria.md](../../../../../../docs/verify-rust-std/challenges/0013-cstr/success-criteria.md)
- Planner record: [planner.md](../../../../../../docs/verify-rust-std/challenges/0013-cstr/planner.md)
- Generator record: [generator.md](../../../../../../docs/verify-rust-std/challenges/0013-cstr/generator.md)
- Evaluator record: [evaluator.md](../../../../../../docs/verify-rust-std/challenges/0013-cstr/evaluator.md)
- Branch-local rubric: [rubric.md](../../../../../../docs/verify-rust-std/challenges/0013-cstr/rubric.md)

Challenge-local artifact contract:

- Keep harnesses, proof entrypoints, expected output, and supporting files in
  this directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Current coverage snapshot:

- `from_ptr.rs`: frontier reached, with `test_from_ptr` and
  `test_index_range_from_exact_bytes`
- `from_bytes_with_nul_unchecked.rs`: frontier reached, with
  `test_from_bytes_with_nul_unchecked_ok`
- `clone_to_uninit.rs`: blocked on the shared
  `core::ffi::CStr::from_bytes_with_nul` donor-link/body frontier
- Missing branch-local coverage still includes the nine safe methods, `strlen`,
  and the remaining invariant/trait proof slices listed in
  [success-criteria.md](../../../../../../docs/verify-rust-std/challenges/0013-cstr/success-criteria.md)

Current blocker:

- Donor-linked SMIR item qualification rewrites the unqualified proof roots
  before `make_call_config` resolves them, so `test_clone_to_uninit` and
  `test_clone_to_uninit_exact_bytes` cannot reach the donated constructor body
  yet.

Status board:

- Planner: active
- Generator: active
- Evaluator: active
- Draft PR: open
