# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the challenge requirements, then retarget the next probe so it isolates `digits_to_dec_str` without the wrapper-level slice-index artifact that blocked the first run.

Next generator task:
- Build and rerun one follow-up challenge-local probe for `digits_to_dec_str` that avoids `Range<usize>::index`, and capture whether the next failure moves into the float-sensitive core or reveals a different missing precondition.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result is still wrapper-artifact-bound or has advanced into the actual `flt2dec` body.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Replace the probe's slice-index-heavy wrapper with a narrower `digits_to_dec_str` harness that bypasses `SliceIndex::index`.
3. Rerun that probe and record the first concrete boundary it reaches.

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces the known float-value backend gap with direct evidence.
- Stop at `in progress` if the follow-up probe reaches further into `flt2dec` and yields a concrete next slice.
- Do not widen scope until the wrapper-level slice-index artifact has been removed from the probe path.
