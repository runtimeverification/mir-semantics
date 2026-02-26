# Plan: Comprehensive Test Coverage for MIR Semantics

## Phase 1 — Coverage Matrix Construction

- [x] 2e83c52 Task: Enumerate execution-relevant sections from Rust Reference and Stable MIR Reference
    - [x] Extract all sections from Rust Reference: Types, Expressions, Statements, Patterns, Type System, Memory Model, Unsafety, Panic, Constant Evaluation
    - [x] Extract Stable MIR structural elements: RValue variants, Operand types, Place projections, Terminator kinds, CastKind, BinOp, UnaryOp, TyKind variants
    - [x] Create initial `docs/coverage-matrix.json` skeleton with one entry per section

- [x] 2e83c52 Task: Map existing mir-semantics tests to Reference sections
    - [x] Classify each prove-rs/ test file by Reference section(s) it exercises
    - [x] Classify each exec-smir/ test file
    - [x] Classify each run-rs/ test file
    - [x] Classify each ub/ test file
    - [x] Populate `tests` entries in `coverage-matrix.json`

- [x] 2e83c52 Task: Map external suite tests to Reference sections
    - [x] Clone Miri tests/pass/ and tests/fail/ — classify tests by Reference section
    - [x] Browse Rust tests/ui (run-pass subset) — classify tests by Reference section
    - [x] Browse Kani tests/kani/ — classify tests by Reference section
    - [x] Populate `tests` and `skip` entries in `coverage-matrix.json`

- [x] 2e83c52 Task: Write coverage report script
    - [x] Create `scripts/coverage-report.py` that reads `coverage-matrix.json`
    - [x] Output summary: sections covered / partial / gap counts
    - [x] Output per-suite stats and top gap areas

- [x] 2e83c52 Task: Verify coverage matrix completeness (Gate)
    - [x] Every execution-relevant Rust Reference section has an entry in coverage-matrix.json
    - [x] Every Stable MIR element (RValue, Terminator, CastKind, BinOp, TyKind variants) is mapped to at least one section
    - [x] Every existing test file (prove-rs/, exec-smir/, run-rs/, ub/) appears in at least one section's `tests`
    - [x] Every imported test file appears in at least one section's `tests` or `skip`
    - [x] Unmapped sections have documented rationale (out-of-scope in spec)

- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2 — Test Suite Import Infrastructure

- [x] 2e83c52 Task: Create suite download/fetch scripts
    - [x] Write `scripts/fetch-miri-tests.sh` to clone Miri at pinned commit and copy tests/pass/ and tests/fail/
    - [x] Write `scripts/fetch-ui-run-pass.sh` to extract run-pass tests from rust-lang/rust tests/ui/
    - [x] Write `scripts/fetch-kani-tests.sh` to clone Kani at pinned commit and copy tests/kani/
    - [x] Add `.gitignore` entries for imported suite directories
    - [x] Add `make fetch-test-suites` target to Makefile
    - [x] Pin all external suites to specific commits in `deps/` or a manifest file

- [x] 2e83c52 Task: Create pytest harness for Miri pass suite
    - [x] Create `kmir/src/tests/integration/data/miri-pass/` directory structure
    - [x] Create `test_miri_pass.py` that reads skip list from `coverage-matrix.json`
    - [x] Verify harness runs: skipped tests skip, non-skipped tests execute

- [x] 2e83c52 Task: Create pytest harness for Miri fail suite
    - [x] Create `kmir/src/tests/integration/data/miri-fail/` directory structure
    - [x] Create `test_miri_fail.py` that reads skip list from `coverage-matrix.json`
    - [x] Verify harness runs

- [x] 2e83c52 Task: Create pytest harness for Rust ui run-pass suite
    - [x] Create `kmir/src/tests/integration/data/ui-run-pass/` directory structure
    - [x] Write filtering logic to select only `//@ run-pass` tests
    - [x] Create `test_ui_run_pass.py` that reads skip list from `coverage-matrix.json`
    - [x] Verify harness runs

- [x] 2e83c52 Task: Create pytest harness for Kani suite
    - [x] Create `kmir/src/tests/integration/data/kani/` directory structure
    - [x] Create `test_kani.py` that reads skip list from `coverage-matrix.json`
    - [x] Verify harness runs

- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3 — Triage and Baseline

- [x] 6fb25c2 Task: Run Miri pass suite and establish baseline
    - [x] Execute full Miri pass suite (skip list from JSON)
    - [x] Record pass/fail counts, categorize failures by Reference section
    - [x] Move newly discovered failing tests to `skip` in `coverage-matrix.json`

- [x] 6fb25c2 Task: Run ui run-pass suite and establish baseline
    - [x] Execute filtered ui run-pass suite
    - [x] Record pass/fail counts
    - [x] Update `coverage-matrix.json`

- [x] 6fb25c2 Task: Run Kani suite and establish baseline
    - [x] Execute Kani suite
    - [x] Record pass/fail counts
    - [x] Update `coverage-matrix.json`

- [x] 2e83c52 Task: Produce consolidated coverage report
    - [x] Run `scripts/coverage-report.py` to generate full report
    - [x] Identify top gap areas ranked by number of skipped/missing tests
    - [x] Estimate complexity (easy/medium/hard) for each gap area
    - [x] Document prioritized gap list for future tracks

- [~] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
    - [x] 2026-02-26 remote no-timeout monitor started: `ui-run-pass --workers 4 --max-depth 300 --case-timeout 0`.
    - [x] 2026-02-26 progress snapshot: `max_completed=82/4859`, reasons `proof_failed=45`, `compile_failed=20`, `policy_skip=14`, `passed=0` (still running).
    - [x] 2026-02-26 simple probe (UI): `--suite ui-run-pass --match nil-pattern.rs --max-depth 500 --case-timeout 0` -> `total=1 passed=1`, `status=PASSED`, `linear_chain=true`.
    - [x] 2026-02-26 simple probe (Miri): `--suite miri-pass --match bools.rs --max-depth 1000 --case-timeout 0` -> `total=1 passed=1`, `status=PASSED`, `linear_chain=true`.
    - [x] 2026-02-26 installed background sampler `/tmp/monitor-ui-no-timeout.sh` (60s cadence) writing `/tmp/ui-run-pass-no-timeout-w4-monitor.log`.
    - [x] 2026-02-26 sampler latest snapshot: `completed=90/4859`, reasons `proof_failed=49`, `compile_failed=20`, `policy_skip=14`, `passed=0` (still running).
    - [x] 2026-02-26 sampler follow-up snapshot: `completed=91/4859`, reasons `proof_failed=50`, `compile_failed=20`, `policy_skip=14`, `passed=0` (still running).
    - [x] 2026-02-26 sampler follow-up snapshot: `completed=96/4859`, reasons `proof_failed=52`, `compile_failed=20`, `policy_skip=14`, `passed=0` (still running).
    - [x] 2026-02-26 fixed UI edition normalization: `edition: 2015..2021` no longer emits invalid `--edition` compile failure (now normalized then classified as `policy_skip` when unsupported).
    - [x] 2026-02-26 compile boundary classification added: stable/toolchain/aux compile errors now mapped to `policy_skip` instead of `compile_failed`.
    - [x] 2026-02-26 targeted remote re-checks:
        - `allocator/custom-in-block.rs`, `allocator/xcrate-use.rs` -> `policy_skip` (`aux-unsupported:E0463`)
        - `box/thin_align.rs`, `box/thin_drop.rs` -> `policy_skip` (`probe-rustc-panic`)
        - `associated-const-range-match-patterns.rs` -> `policy_skip` (`probe-unsupported:E0783`), no invalid edition error.
    - [x] 2026-02-26 restarted no-timeout full run with patched script; early snapshots: `completed=38/4859`, reasons `proof_failed=26`, `policy_skip=10`, `compile_failed=0`.

## Phase 4 — Rustlantis Integration

- [x] 2e83c52 Task: Set up Rustlantis MIR generation infrastructure
    - [x] Research Rustlantis build/run requirements
    - [x] Write `scripts/generate-rustlantis.sh` to generate N random MIR programs
    - [x] Create `kmir/src/tests/integration/data/rustlantis/` directory structure

- [x] 6fb25c2 Task: Create pytest harness for Rustlantis programs
    - [x] Create `test_rustlantis.py` with seed-based parameterization
    - [x] Run initial batch and record baseline results
    - [x] Update `coverage-matrix.json` with Rustlantis findings

- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5 — Documentation

- [x] 2e83c52 Task: Document test coverage workflow
    - [x] Write `docs/dev/test-coverage.md` explaining the coverage-matrix.json approach
    - [x] Document how to un-skip tests, update baselines, and add new suites
    - [x] Document how `coverage-report.py` works

- [ ] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)
