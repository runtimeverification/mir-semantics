# Product Guidelines

## Documentation Tone
- **Technical but accessible:** Documentation should be precise enough for formal
  methods practitioners while remaining readable for developers onboarding to the
  project.
- Favor clear explanations over jargon. Define domain-specific terms (K Framework
  concepts, MIR constructs) on first use in a document.
- Code examples are preferred over lengthy prose when illustrating behavior.

## Code Contribution Standards

### Python Code
- All code must pass `mypy` with `disallow_untyped_defs` enabled — no untyped
  function signatures.
- Follow `black` formatting (line length 120), `isort` import ordering, and
  `flake8` linting without exceptions.
- Run `make format && make check` before submitting changes.

### K Semantics
- Rules must match specific data constructors. Never use catch-all patterns that
  could silently handle unexpected data.
- Execution must get stuck on unimplemented features or unexpected data rather
  than silently continuing with incorrect results. This makes gaps in coverage
  explicit and debuggable.
- Use `seqstrict` for parameter evaluation where needed; declare `Evaluation`
  sort for arguments requiring evaluation.

### Testing
- Every new MIR feature, intrinsic, or operation must include corresponding
  prove-rs test cases before merging.
- Test naming convention: `test-name.rs` for passing tests,
  `test-name-fail.rs` for expected failures.
- Integration tests require both `stable-mir-json` and `build` to be current.

## PR Quality Gates
- `make check` must pass (flake8, mypy, black, isort)
- `make test-unit` must pass
- `make test-integration` must pass for changes touching K semantics or
  the Python-K bridge

## Design Principles
- **Correctness over convenience:** Prefer getting stuck over producing
  wrong results. A stuck execution is a clear signal; a wrong result is
  a hidden bug.
- **Incremental coverage:** Expand MIR support one construct at a time,
  with tests validating each addition.
- **Minimal abstractions:** Only introduce helpers or utilities when
  there is clear reuse. Three similar lines are better than a premature
  abstraction.
