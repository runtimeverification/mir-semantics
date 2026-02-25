# Plan: Comprehensive Test Coverage for MIR Semantics

## Phase 1 — Coverage Matrix Construction

- [ ] Task: Enumerate execution-relevant sections from Rust Reference and Stable MIR Reference
    - [ ] Extract all sections from Rust Reference: Types, Expressions, Statements, Patterns, Type System, Memory Model, Unsafety, Panic, Constant Evaluation
    - [ ] Extract Stable MIR structural elements: RValue variants, Operand types, Place projections, Terminator kinds, CastKind, BinOp, UnaryOp, TyKind variants
    - [ ] Create initial `docs/coverage-matrix.json` skeleton with one entry per section

- [ ] Task: Map existing mir-semantics tests to Reference sections
    - [ ] Classify each prove-rs/ test file by Reference section(s) it exercises
    - [ ] Classify each exec-smir/ test file
    - [ ] Classify each run-rs/ test file
    - [ ] Classify each ub/ test file
    - [ ] Populate `tests` entries in `coverage-matrix.json`

- [ ] Task: Map external suite tests to Reference sections
    - [ ] Clone Miri tests/pass/ and tests/fail/ — classify tests by Reference section
    - [ ] Browse Rust tests/ui (run-pass subset) — classify tests by Reference section
    - [ ] Browse Kani tests/kani/ — classify tests by Reference section
    - [ ] Populate `tests` and `skip` entries in `coverage-matrix.json`

- [ ] Task: Write coverage report script
    - [ ] Create `scripts/coverage-report.py` that reads `coverage-matrix.json`
    - [ ] Output summary: sections covered / partial / gap counts
    - [ ] Output per-suite stats and top gap areas

- [ ] Task: Verify coverage matrix completeness (Gate)
    - [ ] Every execution-relevant Rust Reference section has an entry in coverage-matrix.json
    - [ ] Every Stable MIR element (RValue, Terminator, CastKind, BinOp, TyKind variants) is mapped to at least one section
    - [ ] Every existing test file (prove-rs/, exec-smir/, run-rs/, ub/) appears in at least one section's `tests`
    - [ ] Every imported test file appears in at least one section's `tests` or `skip`
    - [ ] Unmapped sections have documented rationale (out-of-scope in spec)

- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2 — Test Suite Import Infrastructure

- [ ] Task: Create suite download/fetch scripts
    - [ ] Write `scripts/fetch-miri-tests.sh` to clone Miri at pinned commit and copy tests/pass/ and tests/fail/
    - [ ] Write `scripts/fetch-ui-run-pass.sh` to extract run-pass tests from rust-lang/rust tests/ui/
    - [ ] Write `scripts/fetch-kani-tests.sh` to clone Kani at pinned commit and copy tests/kani/
    - [ ] Add `.gitignore` entries for imported suite directories
    - [ ] Add `make fetch-test-suites` target to Makefile
    - [ ] Pin all external suites to specific commits in `deps/` or a manifest file

- [ ] Task: Create pytest harness for Miri pass suite
    - [ ] Create `kmir/src/tests/integration/data/miri-pass/` directory structure
    - [ ] Create `test_miri_pass.py` that reads skip list from `coverage-matrix.json`
    - [ ] Verify harness runs: skipped tests skip, non-skipped tests execute

- [ ] Task: Create pytest harness for Miri fail suite
    - [ ] Create `kmir/src/tests/integration/data/miri-fail/` directory structure
    - [ ] Create `test_miri_fail.py` that reads skip list from `coverage-matrix.json`
    - [ ] Verify harness runs

- [ ] Task: Create pytest harness for Rust ui run-pass suite
    - [ ] Create `kmir/src/tests/integration/data/ui-run-pass/` directory structure
    - [ ] Write filtering logic to select only `//@ run-pass` tests
    - [ ] Create `test_ui_run_pass.py` that reads skip list from `coverage-matrix.json`
    - [ ] Verify harness runs

- [ ] Task: Create pytest harness for Kani suite
    - [ ] Create `kmir/src/tests/integration/data/kani/` directory structure
    - [ ] Create `test_kani.py` that reads skip list from `coverage-matrix.json`
    - [ ] Verify harness runs

- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3 — Triage and Baseline

- [ ] Task: Run Miri pass suite and establish baseline
    - [ ] Execute full Miri pass suite (skip list from JSON)
    - [ ] Record pass/fail counts, categorize failures by Reference section
    - [ ] Move newly discovered failing tests to `skip` in `coverage-matrix.json`

- [ ] Task: Run ui run-pass suite and establish baseline
    - [ ] Execute filtered ui run-pass suite
    - [ ] Record pass/fail counts
    - [ ] Update `coverage-matrix.json`

- [ ] Task: Run Kani suite and establish baseline
    - [ ] Execute Kani suite
    - [ ] Record pass/fail counts
    - [ ] Update `coverage-matrix.json`

- [ ] Task: Produce consolidated coverage report
    - [ ] Run `scripts/coverage-report.py` to generate full report
    - [ ] Identify top gap areas ranked by number of skipped/missing tests
    - [ ] Estimate complexity (easy/medium/hard) for each gap area
    - [ ] Document prioritized gap list for future tracks

- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4 — Rustlantis Integration

- [ ] Task: Set up Rustlantis MIR generation infrastructure
    - [ ] Research Rustlantis build/run requirements
    - [ ] Write `scripts/generate-rustlantis.sh` to generate N random MIR programs
    - [ ] Create `kmir/src/tests/integration/data/rustlantis/` directory structure

- [ ] Task: Create pytest harness for Rustlantis programs
    - [ ] Create `test_rustlantis.py` with seed-based parameterization
    - [ ] Run initial batch and record baseline results
    - [ ] Update `coverage-matrix.json` with Rustlantis findings

- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5 — Documentation

- [ ] Task: Document test coverage workflow
    - [ ] Write `docs/dev/test-coverage.md` explaining the coverage-matrix.json approach
    - [ ] Document how to un-skip tests, update baselines, and add new suites
    - [ ] Document how `coverage-report.py` works

- [ ] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)
