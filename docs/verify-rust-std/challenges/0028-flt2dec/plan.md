# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the published success criteria table, then reduce the new `core::slice::index` frontier at `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` (`library/core/src/slice/index.rs:440`) to the smallest challenge-local reproducer that still preserves the post-select path.

Next generator task:
- Keep the restored real prefix slice `&buf[..exp]`, keep the suffix stub in place, and trim only the current post-select slice-index path so the next replay still preserves the challenge-local frontier while shrinking the reproducer.

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

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces a real backend float gap with direct evidence after the `buf.len()` branch test has been simplified away.
- Stop at `in progress` if the follow-up probe reaches further into the decimal-point path and yields a concrete next slice beyond the copied `if exp >= buf.len()` select.
- Do not widen scope to restore the real suffix slice or other operations until the first post-select leaf has been captured with evidence.
