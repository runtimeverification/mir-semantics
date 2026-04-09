# Evaluator Record: Challenge 0001

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0001-core-transmutation.md
- Tracking issue: [#19](https://github.com/model-checking/verify-rust-std/issues/19)
- Planner record: `docs/verify-rust-std/challenges/0001-core-transmutation/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0001-core-transmutation/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0001-core-transmutation/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Spec-book guidance for transmutation exists and is referenced | 0 | none yet | No updated spec-book entry or challenge-local reference has been identified. |
| Coverage threshold is evidenced for the published target set | 0 | none yet | No coverage table or count has been recorded for the 35/47 threshold. |
| In-scope transmutation APIs have faithful contracts | 0 | none yet | No contracts or explicit blockers have been collected for the in-scope APIs. |
| Safe wrappers are wrapped with local assumptions and assertions | 0 | none yet | No proof harnesses or annotated call sites are available for review. |
| Excluded categories stay explicitly excluded | 0 | none yet | No evidence yet shows the excluded families are either untouched or explicitly justified. |
| Evidence bundles are reproducible | 0 | none yet | No commands, target files, or expected-output logs have been captured. |
| Review feedback patterns are incorporated | 0 | none yet | Only one relevant prior review cue has been collected, and it has not yet been reflected in artifacts. |
| Residual risk is explicit | 0 | none yet | No blocker log exists yet, so missing support would currently be implicit. |

## Review Pattern Notes

- Prior solution PR review cue from `runtimeverification/mir-semantics#985`:
  keep test and artifact names distinct across challenge directories, and make
  blockers explicit rather than leaving them to inference.
- Reviewer-facing writeups should separate delivered evidence from blocked
  scope so a reviewer can tell what was proven, what was deferred, and why.
- For this challenge, the reviewer will likely expect a countable artifact map
  rather than a narrative-only summary.

## Likely Reviewer Concerns

- The challenge is still at bootstrap stage, so any claim of coverage without
  concrete files and commands would be unsupported.
- The published success criteria require a 35-of-47 coverage threshold, so a
  reviewer will look for an explicit accounting table and may reject vague
  statements like "most methods are covered."
- The challenge excludes several transmute-heavy families, so the evaluator
  should fail closed if the branch silently omits them instead of naming the
  exclusion.
- If the solution leans on `Transmutability`, the reviewer will want proof that
  any required upstream impl changes are either already landed or still blocked.

## Verdict

- Current status: `not started`
- Current verdict: `not started`
- Rationale: no implementation evidence, challenge-local artifacts, or rerun
  commands have been recorded yet.

## Iteration Log

- Bootstrap record created by orchestrator.
- Challenge-specific rubric and evaluator skeleton added; no evidence collected
  yet.
