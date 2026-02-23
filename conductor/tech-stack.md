# Technology Stack

## Core Languages & Frameworks
- **Python (>=3.10)** — Frontend CLI tool (`kmir`), build system `hatchling`, managed by `uv`
- **K Framework** — Formal semantics engine, definitions in literate Markdown (`.md`)
  - Version pinned in `deps/k_release`
- **Rust (nightly)** — Target language for verification
  - `stable-mir-json` submodule for SMIR extraction; version pinned in `deps/stable-mir-json_release`
  - Rust toolchain version specified in `deps/stable-mir-json/rust-toolchain.toml`

## Build & Package Management
- **uv** — Python package manager and runner; version pinned in `deps/uv_release`
- **Make** — Build orchestration (`Makefile`)
- **Cargo** — Rust build tool (for `stable-mir-json`)

## Testing
- **pytest** — Test framework
- **pytest-xdist** — Parallel test execution
- **pytest-cov** — Coverage reporting

## Linting & Formatting
- **flake8** — Python linting
- **mypy** — Static type checking
- **black** — Code formatting (line length 120)
- **isort** — Import ordering
- **autoflake** — Unused import removal

## Infrastructure
- **GitHub Actions** — CI/CD
- **Nix** — Reproducible builds and formatting
- **Git submodules** — Dependency management (`stable-mir-json`)

## Version Management
All external dependency versions are pinned in the `deps/` directory:
- `deps/k_release` — K Framework version
- `deps/stable-mir-json_release` — stable-mir-json commit hash
- `deps/uv_release` — uv version
