# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the published success criteria table, then keep the current challenge-local reproducer at the `core::slice::index` frontier `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` (`library/core/src/slice/index.rs:440`) unless a smaller reproducer can preserve the same post-select path.

Next generator task:
- Re-run the existing proof/show evidence against the current challenge-local probe, then stop shrinking if the first leaf is still the `Range<usize>::index` frontier; otherwise record the newly smaller reproducer and its exact first leaf.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode, now from a replay-based collector that asserts the current probe replay fails at the slice-index frontier.
- A note saying whether the result stays in copied `digits_to_dec_str` control flow, advances into actual decimal-point-path logic, or exposes a genuine backend limit.
- A pointer back to `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md` so the probe evidence is auditable against the published function list.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Preserve the restored real prefix slice and the single concrete `digits_to_dec_str` case, but trim only the current post-select slice-index path so the active path stays challenge-local.
3. Rerun only that minimally trimmed probe and record the first concrete boundary it reaches, classifying it as copied `flt2dec` control flow, decimal-point-path logic, a backend limit, or the underlying slice-index helper.
4. If the frontier moves past `slice_end_index_len_fail`, keep the smallest discovered reproducer and update the success-criteria coverage notes to reflect the new proof frontier rather than shrinking again.

Stop conditions:
- Stop at `blocked` only if a smaller reproducer exposes a new backend or library boundary with direct evidence after the `buf.len()` branch test has been simplified away.
- Stop at `in progress` if the replay still lands on `slice_end_index_len_fail` at `Range<usize>::index` and no smaller challenge-local reproducer is found.
- Do not widen scope to restore the real suffix slice or other operations until the first post-select leaf has been captured with evidence.
