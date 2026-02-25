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
make test-rustlantis
```

All external harnesses:

- discover `*.rs` files from `kmir/src/tests/integration/data/<suite>/`
- verify every discovered file is listed in matrix `tests` or `skip`
- skip test cases listed in matrix `skip`

## Rustlantis Corpus

Generate a deterministic corpus (default seeds from `0`):

```bash
./scripts/generate-rustlantis.sh --count 10 --seed-start 0
```

Optional SMIR generation:

```bash
./scripts/generate-rustlantis.sh --count 10 --seed-start 0 --with-smir
```

Then map each generated `rustlantis/seed-*.rs` path into matrix `tests` or `skip`.

## Triage Loop

When running any external suite target:

1. Run the target.
2. For newly failing files, move/add entries to `skip`.
3. For newly passing files, move entries from `skip` to `tests`.
4. Re-run `scripts/coverage-report.py --validate`.

This keeps matrix metadata and harness behavior synchronized.

## Remote Execution Protocol (`zhaoji`)

Local code editing stays in the worktree. Gate/test execution runs remotely:

```bash
rsync -az --delete \
  --exclude '.git' \
  --exclude 'kmir/.venv' \
  --exclude '.pytest_cache' \
  --exclude '__pycache__' \
  --exclude 'deps/stable-mir-json/' \
  /Users/steven/.codex/worktrees/b1dc/mir-semantics/ \
  zhaoji:/home/zhaoji/projs/mir-semantics-b1dc/

ssh zhaoji 'cd /home/zhaoji/projs/mir-semantics-b1dc && \
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" && \
  <CMD>'
```

Stop immediately on any non-zero gate command.
