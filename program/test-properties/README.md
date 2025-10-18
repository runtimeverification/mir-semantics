# SPL Token Program Formal Verification Guide

## Architecture

- **Production code**: `src/entrypoint.rs` - Used for normal builds
- **Runtime verification code (Original Version)**: `src/entrypoint-rvo.rs` - Used when `rvo` feature is enabled. This version is to be tested by the original spl token tests.
- **Runtime verification code**: `src/entrypoint-runtime-verification.rs` - Used when `runtime-verification` feature is enabled. This version is constrained and constructed with formal verification in mind.

## Setup test environment

1. Make sure you can pass the original tests in the root directory:
```sh
pnpm programs:build && pnpm programs:test
```
2. Check if the specs in `program/entrypoint-rvo.rs` are passing with the same tests (important step after adding new specs):
```sh
pnpm programs:build -- --features rvo && pnpm programs:test -- --features rvo
```

## Scripts
- `./scripts/compare-test-functions.py` - Compares matching `test_*` functions between the runtime verification entrypoints and highlights differences or missing tests. Run it directly (`./scripts/compare-test-functions.py`) to diff `p-token/src/entrypoint-runtime-verification.rs` against both `program/src/entrypoint-rvo.rs` and `program/src/entrypoint-runtime-verification.rs`. Use `--rvo` or `--rv` to limit the report to a single target, and pass extra pairs with `--pairs left:path:right:path` when you need custom comparisons.
- [`program/test-properties/scripts/sync-spl-specs.py`](scripts/sync-spl-specs.py) - Regenerates the SPL harnesses from the Pinocchio (p-token) source using the transform config in [`program/test-properties/scripts/sync_spl_specs_config.json`](scripts/sync_spl_specs_config.json).

## Syncing SPL specs from p-token

The SPL entrypoint harnesses are derived from the Pinocchio (`p-token`) implementation so the two stay behaviourally aligned. The transformation pipeline is implemented in [`program/test-properties/scripts/sync-spl-specs.py`](scripts/sync-spl-specs.py#L46) and is driven entirely by declarative edits captured in [`program/test-properties/scripts/sync_spl_specs_config.json`](scripts/sync_spl_specs_config.json).

High-level flow:
- `main` ([`scripts/sync-spl-specs.py#L46`](scripts/sync-spl-specs.py#L46)) loads the JSON config, parses the Pinocchio harness source file listed in the config, and orchestrates the regeneration process.
- `assemble_sections` ([`scripts/sync-spl-specs.py#L64`](scripts/sync-spl-specs.py#L64)) iterates over every configured harness, delegating to `transform_harness` to rewrite each Pinocchio `test_process_*` into the SPL form while collecting the match-arm metadata.
- `transform_harness` ([`scripts/sync-spl-specs.py#L101`](scripts/sync-spl-specs.py#L101)) coordinates the conversion by: splitting the original snippet, rewriting the signature/Accounts line, normalising the function body, and rendering the final text. The helpers `_prepare_body_lines` ([`scripts/sync-spl-specs.py#L205`](scripts/sync-spl-specs.py#L205)) and `_render_harness` ([`scripts/sync-spl-specs.py#L260`](scripts/sync-spl-specs.py#L260)) are where comment-outs, replacements, and prologue/epilogue wiring occur.
- `render_template` ([`scripts/sync-spl-specs.py#L83`](scripts/sync-spl-specs.py#L83)) inserts the generated harness blocks and match arms into the SPL entrypoint template path specified in the config.

Output layout:
- The script reads the template at [`program/test-properties/templates/runtime_entrypoint.rs`](templates/runtime_entrypoint.rs) and replaces the placeholders `// === AUTO-GENERATED MATCH ARMS ===` and `// === AUTO-GENERATED HARNESS FUNCTIONS ===` defined in the config (`sync_spl_specs_config.json`).
- Match arms are rendered from [`MATCH_ARM_TEMPLATE`](scripts/sync-spl-specs.py#L35) and spliced into the `match` statement that dispatches instructions.
- Each regenerated harness comprises:
  - Preserved doc comments/attributes collected in `_collect_header_metadata`.
  - A rewritten signature that fixes the `accounts` argument and instruction types (`_build_signature`).
  - A standard prologue and epilogue injected by [`_build_prologue`](scripts/sync-spl-specs.py#L237) and [`_build_epilogue`](scripts/sync-spl-specs.py#L251) to set the discriminator/program ID and to assert the instruction buffer is unchanged.
  - The body segment from Pinocchio after applying comment-out and replacement directives (`_prepare_body_lines`).

To regenerate the SPL harnesses after editing the config or upstream Pinocchio code:

```sh
python3 program/test-properties/scripts/sync-spl-specs.py
```

The script will rewrite the target file referenced in the config (currently `program/src/entrypoint-rvo.rs`) and print a summary of the applied transforms. Always review the resulting diff to ensure the declarative edits captured the intended behaviour.
