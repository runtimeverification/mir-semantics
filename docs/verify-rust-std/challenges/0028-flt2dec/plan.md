# Execution Plan: Challenge 0028

Current objective:
- Reconfirm the challenge requirements, then treat the saved taken-arm artifact as cleared scaffolding and retarget the next probe so it advances from `#EndProgram ~> .K` into the smallest remaining `flt2dec`-owned successor path, without reopening the copied-function guard and branch-select setup.

Next generator task:
- Keep the `b"1234", exp = 2, frac_digits = 3` case and the taken-arm specialization, but replace the branch-select-only target with the narrowest challenge-local probe that reaches the next unproven `flt2dec`-owned step after the terminal `#EndProgram ~> .K` leaf, rather than restoring any of the already-cleared wrapper guards or raw-slice helpers.

Generator acceptance evidence:
- The probe file path in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`.
- The exact command(s) used to rerun it.
- The first pass/fail result with the precise failure mode.
- A note saying whether the result stays at the taken-arm `#EndProgram ~> .K` artifact, advances into actual `flt2dec` body logic, or exposes a genuine backend limit.

Plan slices:
1. Reconfirm the published function list, safety obligations, and UB exclusions from the challenge page.
2. Preserve the taken-arm specialization for the single concrete `digits_to_dec_str` case, but narrow the probe to the first unproven `flt2dec`-owned successor after the terminal `#EndProgram ~> .K` leaf, avoiding any return to the copied wrapper guards or branch-select scaffolding.
3. Rerun only that minimally generalized probe and record the first concrete boundary it reaches, classifying it as `flt2dec`-owned logic or a backend limit once it actually leaves the already-cleared taken-arm artifact.

Stop conditions:
- Stop at `blocked` only if the follow-up probe reproduces a real backend float gap with direct evidence from the new successor path.
- Stop at `in progress` if the follow-up probe reaches further into `flt2dec` and yields a concrete next slice beyond the cleared `#EndProgram ~> .K` artifact.
- Do not widen scope until the next post-terminal leaf has been captured with evidence and the probe has stayed out of the already-cleared branch-select scaffolding.
