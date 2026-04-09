# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the challenge requirements, then retarget the next probe so it removes the raw-slice construction artifact that now blocks the narrowed `digits_to_dec_str` path.

Next generator task:
- Build and rerun one follow-up challenge-local probe for `digits_to_dec_str` that avoids `split_at_raw` / `std::slice::from_raw_parts`, and capture the first boundary it reaches after raw-slice construction is gone.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result is still wrapper-artifact-bound or has advanced into the actual `flt2dec` body.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Replace the probe's raw-slice helper with a narrower `digits_to_dec_str` harness that does not call `split_at_raw` or `from_raw_parts`.
3. Rerun that probe and record the first concrete boundary it reaches.

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces the known float-value backend gap with direct evidence.
- Stop at `in progress` if the follow-up probe reaches further into `flt2dec` and yields a concrete next slice.
- Do not widen scope until the raw-slice construction artifact has been removed from the probe path.
