# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the published success criteria table, then retarget the next probe from the restored-prefix frontier at the copied `if exp >= buf.len()` branch in `digits_to_dec_str_probe.rs:76` so the same single case advances past that control-flow test without widening beyond one exact simplification target.

Next generator task:
- Keep the restored real prefix slice `&buf[..exp]`, keep the suffix stub in place, and rewrite only the copied `if exp >= buf.len()` check so `buf.len()` is fixed to the concrete single-case value for `b"1234", exp = 2`; then rerun and capture the first leaf beyond that branch select.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result stays in copied `digits_to_dec_str` control flow after the `buf.len()` simplification, advances into actual decimal-point-path logic, or exposes a genuine backend limit.
- A pointer back to `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md` so the probe evidence is auditable against the published function list.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Preserve the restored real prefix slice and the single concrete `digits_to_dec_str` case, but simplify only the copied `if exp >= buf.len()` control-flow test so the active path no longer depends on `#applyUnOp ( unOpPtrMetadata , ... )` for `buf.len()`.
3. Rerun only that minimally simplified probe and record the first concrete boundary it reaches, classifying it as copied `flt2dec` control flow, decimal-point-path logic, or a backend limit.

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces a real backend float gap with direct evidence after the `buf.len()` branch test has been simplified away.
- Stop at `in progress` if the follow-up probe reaches further into the decimal-point path and yields a concrete next slice beyond the copied `if exp >= buf.len()` select.
- Do not widen scope to restore the real suffix slice or other operations until the first post-select leaf has been captured with evidence.
