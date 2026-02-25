# Track: Comprehensive Test Coverage for MIR Semantics

## Overview

Systematically expand the mir-semantics test suite to cover all execution-relevant features
described in the official Rust Reference, by importing established external test suites
(Miri, Rust compiler ui/run-pass, Kani, Rustlantis) as separate test directories and
building a coverage matrix that maps every relevant Reference section to concrete test files.

## Background

### Current State
The mir-semantics project has ~300+ test cases across:
- `prove-rs/` (82 Rust files) — symbolic proof tests
- `exec-smir/` (39 files) — concrete SMIR execution tests
- `run-rs/` (34 files) — Rust execution tests
- `crate-tests/` (29 projects) — multi-crate linking tests
- `ub/` (5 files) — undefined behavior detection tests

These tests cover core types, arithmetic, control flow, pointers, closures, and intrinsics,
but coverage is organic — there is no systematic mapping to the Rust Reference and significant
gaps likely exist (e.g., advanced pattern matching, type coercions, destructors, const eval).

### Reference Project
The `formal-semantics` project uses a disciplined approach: every section of the target
language reference maps to a plan item with associated tests. Tests are sourced from official
suites first, with hand-written tests only for uncovered features.

## Functional Requirements

### FR-1: Coverage Matrix (`docs/coverage-matrix.json`)
Build a single JSON file as the source of truth for test coverage, mapping every
execution-relevant section of the Rust Reference and Stable MIR Reference to test files.

**Schema:**
```json
{
  "sections": {
    "<section-path>": {
      "rust_ref": "<url>",
      "smir_elements": ["<Stable MIR type/variant>", ...],
      "tests": {
        "<suite>": ["<test-file>", ...]
      },
      "skip": {
        "<suite>": ["<test-file>", ...]
      }
    }
  }
}
```

- `tests`: test files that pass and exercise this section
- `skip`: test files relevant to this section but not yet passing (un-skip = move to `tests`)
- Coverage status is derived: no tests = gap, has skip = partial, only tests = fully covered
- pytest reads this JSON directly to generate skip lists per suite

**Execution-relevant sections** (from the Rust Reference):
1. **Types** — boolean, numeric (integer, float), textual (char, str), never, tuple, array,
   slice, struct, enum, union, function pointer, closure, pointer (reference, raw),
   function item, trait object
2. **Expressions** — literals, paths, blocks, operators (arithmetic, bitwise, comparison,
   logical, negation, dereference, borrow, assignment, compound assignment), grouped, array,
   tuple, struct, call, method call, field access, closure, loop (loop/while/for), range,
   if/if-let, match, return, await
3. **Statements** — let, expression, item
4. **Patterns** — literal, identifier, wildcard, rest, range, reference, struct, tuple struct,
   tuple, grouped, slice, path, or
5. **Type system** — type layout, interior mutability, type coercions, destructors (Drop),
   dynamically sized types
6. **Memory model** — allocation, lifetime, variables
7. **Unsafety** — behavior considered undefined (all sub-items)
8. **Panic** — unwinding, abort
9. **Constant evaluation** — const contexts, const functions

**Stable MIR elements** to cross-reference:
- RValue variants, Operand types, Place projections, Terminator kinds
- CastKind, BinOp, UnaryOp, NullOp
- TyKind variants, AggregateKind

### FR-2: Import External Test Suites
Import tests from the following sources as separate directories under
`kmir/src/tests/integration/data/`:

| Suite | Source | Directory | Priority |
|-------|--------|-----------|----------|
| Miri pass | `rust-lang/miri/tests/pass/` | `miri-pass/` | P0 |
| Miri fail | `rust-lang/miri/tests/fail/` | `miri-fail/` | P0 |
| Rust ui run-pass | `rust-lang/rust/tests/ui/` (filtered) | `ui-run-pass/` | P1 |
| Kani | `model-checking/kani/tests/kani/` | `kani/` | P1 |
| Rustlantis | Generated programs | `rustlantis/` | P2 |

Each suite must:
- Be gitignored and fetched via script (not committed in bulk)
- Have a pytest harness that reads `coverage-matrix.json` for skip lists
- Be pinned to specific commits

### FR-3: Report Generation
A script (`scripts/coverage-report.py`) reads `coverage-matrix.json` and produces:
- Summary stats: sections covered / partial / gap
- Per-suite pass rates
- Top gap areas ranked by number of skipped tests

## Non-Functional Requirements

- **Non-disruptive**: Existing test directories and test harnesses must not be modified
- **Incremental**: Suites can be imported and classified independently
- **Reproducible**: Suite versions pinned to specific commits
- **Single source of truth**: `coverage-matrix.json` drives both skip lists and reporting

## Acceptance Criteria

1. `docs/coverage-matrix.json` exists with all execution-relevant Rust Reference sections
2. Every section has associated test files mapped (from existing and/or external suites)
3. At least Miri pass suite is imported with working pytest harness reading from the JSON
4. `scripts/coverage-report.py` produces a readable summary
5. Coverage matrix is bidirectionally complete (gate in Phase 1)

## Out of Scope

- Fixing MIR semantics gaps identified by the matrix (future tracks)
- Chapters not relevant to MIR execution: Lexical Structure, Macros, Crates and Source Files,
  Conditional Compilation, Attributes, Names, Linkage, Inline Assembly, ABI, Runtime
- Importing Creusot/Prusti/Verus suites (follow-up track)
- Performance benchmarking
- CI integration for imported suites (follow-up track)
