# Verify Rust Std Re-Execution Portfolio

This branch is the orchestration control plane for re-executing the
`model-checking/verify-rust-std` challenge set from
`runtimeverification/mir-semantics`.

Operating rules:

- The orchestration branch does not carry challenge implementations.
- Each challenge gets its own branch and worktree based on `origin/master`.
- Each challenge branch carries persistent planner, generator, and evaluator
  records under `docs/verify-rust-std/challenges/`.
- Each challenge branch also carries a challenge-local artifact directory under
  `kmir/src/tests/integration/data/verify-rust-std/`.
- The evaluator owns the branch-local rubric snapshot and readiness verdict.
- Cross-challenge patterns are recorded here, then copied or cherry-picked into
  challenge branches only when needed.

Reference inputs:

- Challenge book: `https://github.com/model-checking/verify-rust-std`
- Published rules: `doc/src/general-rules.md`
- Reference implementation pattern: `runtimeverification/mir-semantics#985`

Primary portfolio artifacts:

- `docs/verify-rust-std/portfolio/manifest.tsv`
- `docs/verify-rust-std/portfolio/rubric.md`
- `docs/verify-rust-std/templates/`
- `scripts/verify-rust-std/init-challenge-worktrees.sh`
