# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the challenge requirements, then retarget the next probe so it removes the remaining `MaybeUninit::slice_assume_init_ref` helper artifact that now blocks the narrowed `digits_to_dec_str` path.

Next generator task:
- Rewrite the challenge-local `digits_to_dec_str` probe so its return path no longer calls `MaybeUninit::slice_assume_init_ref` on the temporary `parts` buffer, then rerun the same single `b"1234", exp = 2, frac_digits = 3` case and capture the first leaf it reaches.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result is still wrapper-artifact-bound, has advanced into the actual `flt2dec` body, or has exposed a genuine backend limit.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Replace the probe's `MaybeUninit` slice conversion with a narrower `digits_to_dec_str` harness that returns an already-initialized slice view without calling `slice_assume_init_ref`.
3. Rerun that probe and record the first concrete boundary it reaches.

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces the known float-value backend gap with direct evidence.
- Stop at `in progress` if the follow-up probe reaches further into `flt2dec` and yields a concrete next slice.
- Do not widen scope until the `MaybeUninit::slice_assume_init_ref` artifact has been removed from the probe path.
