# Test Coverage Workflow

This document defines the executable workflow for `docs/coverage-matrix.json`,
external suite imports, and coverage reporting.

## Goals

- Keep `docs/coverage-matrix.json` as the single source of truth for:
  - execution-relevant Rust Reference sections
  - Stable MIR element mapping (`smir_elements`)
  - per-suite `tests` (passing) and `skip` (known gaps)
- Keep default CI-friendly integration test runs small.
- Allow explicit opt-in execution of external suites.
- Prevent architecture-only failures from being mixed with semantic failures in external-suite baselines.

## Coverage Matrix Contract

Each section entry in `docs/coverage-matrix.json` contains:

- `rust_ref`: canonical Rust Reference URL
- `smir_elements`: list of Stable MIR symbols mapped to this section
- `tests`: `{suite: [paths...]}` for passing tests
- `skip`: `{suite: [paths...]}` for relevant but currently non-passing tests
- `note`: rationale text for gaps/partial coverage

Validation is strict:

```bash
uv --project kmir run --python cpython-3.11.13 \
  python scripts/coverage-report.py --validate --summary --suite-stats
```

`--validate` fails if:

- required section keys are missing
- required Stable MIR symbols are unmapped
- existing local suite files are not present in `tests`
- discovered external suite files are not present in `tests` or `skip`
- any gap section misses a non-empty `note`

## External Suite Import

Pinned commits are defined in:

- `deps/miri_release`
- `deps/rust_release`
- `deps/kani_release`
- `deps/rustlantis_release`

Import/update all fetched suites:

```bash
make fetch-test-suites
```

This runs:

- `scripts/fetch-miri-tests.sh`
- `scripts/fetch-ui-run-pass.sh`
- `scripts/fetch-kani-tests.sh`

Imported directories are gitignored under `kmir/src/tests/integration/data/`.

## Test Entry Points

Default integration run excludes external suites:

```bash
make test-integration
```

Explicit external runs:

```bash
make test-miri-pass
make test-miri-fail
make test-ui-run-pass
make test-kani
make test-kani-adapted
make test-rustlantis
```

All external harnesses:

- discover `*.rs` files from `kmir/src/tests/integration/data/<suite>/`
- verify every discovered file is listed in matrix `tests` or `skip`
- skip test cases listed in matrix `skip`

## UI Directive-Aware Execution

`scripts/run-external-suite.py --suite ui-run-pass` now performs a prep phase before `prove-rs`:

- parses `//@` directives, including revision-prefixed directives
- handles `revisions` by generating per-revision sub-cases and aggregating back to one source-file result
- supports `edition`, `compile-flags`, `rustc-env`
- supports `aux-build`, `aux-crate`, and `proc-macro` by compiling auxiliary crates and wiring them through `-L/--extern`
- applies platform gating from `only-*` and `ignore-*` directives
- performs compile-probe before proving to classify architecture/compiler failures explicitly

File-level status for UI is still strict pass criteria:

- `ProofStatus.PASSED`
- linear proof chain

## Rustlantis Corpus

Generate a deterministic corpus (default seeds from `0`) with profile-based size:

```bash
./scripts/generate-rustlantis.sh --profile small --count 20 --seed-start 0
```

Available profiles:

- `small` (default): fast, smaller programs
- `medium`: balanced size
- `large`: deeper programs for stress testing

Convenience targets:

```bash
make rustlantis-small
make rustlantis-medium
make rustlantis-large
```

Optional SMIR generation:

```bash
./scripts/generate-rustlantis.sh --count 10 --seed-start 0 --with-smir
```

Then map each generated `rustlantis/seed-*.rs` path into matrix `tests` or `skip`.

## Kani Deferred Policy

Kani is imported and mapped in coverage matrix, but default gate behavior is deferred:

- `make test-kani` runs with `KMIR_KANI_MODE=deferred` and skips semantic prove cases
- `make test-kani-adapted` enables experimental adapted mode (`KMIR_KANI_MODE=adapted`)
  - strips proof-only Kani attributes
  - runs only cases that do not require `kani::*` runtime APIs
  - cases requiring runtime APIs are classified as policy skips

Coverage/reporting should treat this as a deferred lane (`deferred-not-in-scope`) until full Kani integration is implemented.

## Triage Loop

When running any external suite target:

1. Run the target.
2. For newly failing files, move/add entries to `skip`.
3. For newly passing files, move entries from `skip` to `tests`.
4. Re-run `scripts/coverage-report.py --validate`.

This keeps matrix metadata and harness behavior synchronized.

`scripts/run-external-suite.py` emits:

- `results` (file-level passed/failed/skipped)
- full `reason_histogram` and `detail_histogram`
- sample non-pass cases with reason/detail

Use those histograms to distinguish architecture failures (`prep_failed`, `compile_failed`, `policy_skip`) from semantic failures (`proof_failed`, `non_linear_proof`, `timeout`).

## Remote Execution Protocol (`zhaoji`)

Local code editing stays in the worktree. Gate/test execution runs remotely:

```bash
rsync -az --delete \
  --exclude '.git' \
  --exclude 'kmir/.venv' \
  --exclude '.pytest_cache' \
  --exclude '__pycache__' \
  --exclude 'deps/.stable-mir-json/' \
  --exclude 'deps/stable-mir-json/' \
  /Users/steven/.codex/worktrees/b1dc/mir-semantics/ \
  zhaoji:/home/zhaoji/projs/mir-semantics-b1dc/

ssh zhaoji 'cd /home/zhaoji/projs/mir-semantics-b1dc && \
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" && \
  make stable-mir-json && \
  <CMD>'
```

Stop immediately on any non-zero gate command.
