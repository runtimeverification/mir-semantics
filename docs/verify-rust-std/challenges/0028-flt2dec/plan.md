# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the challenge requirements, then retarget the next probe so it removes the copied-function `if exp < buf.len()` branch select at `digits_to_dec_str_probe.rs:58` and lets the same case advance toward `flt2dec`-owned logic or a genuine backend limit.

Next generator task:
- Make the challenge-local `digits_to_dec_str` probe expose the post-select control flow cheaply: keep the `b"1234", exp = 2, frac_digits = 3` case, but add the smallest possible branch-specific trace or guard so the copied `if exp < buf.len()` `#selectBlock` at `digits_to_dec_str_probe.rs:58` is resolved once and the next leaf after it is captured without another blind full-depth rerun.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result is still wrapper-artifact-bound, has advanced into the actual `flt2dec` body, or has exposed a genuine backend limit.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Specialize the narrowed `digits_to_dec_str` harness so the single concrete case bypasses the copied `if exp < buf.len()` branch select as a blind rerun target and instead lands on the next control-flow step cheaply.
3. Rerun only the minimally instrumented probe and record the first concrete boundary it reaches, classifying it as `flt2dec`-owned logic or a backend limit if it finally escapes the wrapper.

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces the known float-value backend gap with direct evidence.
- Stop at `in progress` if the follow-up probe reaches further into `flt2dec` and yields a concrete next slice.
- Do not widen scope until the copied-function branch-select path has been forced past or the next post-select leaf has been captured with evidence.
