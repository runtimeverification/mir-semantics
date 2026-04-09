# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the challenge requirements, then use one minimal probe to determine whether `flt2dec` immediately hits the same float backend boundary that stalled challenge 0011.

Next generator task:
- Build and rerun a single challenge-local probe for `digits_to_dec_str`, and capture whether the first failure is a backend float-value limitation, an artifact wiring gap, or a missing precondition.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result matches the challenge 0011 float blocker or is distinct.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Execute one minimal probe and record the exact backend or artifact boundary it reaches.
3. Use that result to decide whether the next slice is a broader float decomposition or a blocker report.

Stop conditions:
- Stop at `blocked` if the probe reproduces the known float-value backend gap with direct evidence.
- Stop at `in progress` if the probe succeeds and the challenge can be decomposed further from that concrete starting point.
- Do not widen scope until the first probe has a reproducible result.
