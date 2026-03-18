# MIR Semantics

`mir-semantics` models the semantics of Rust Stable MIR in K. The repository also ships `kmir`, a Python CLI for building the semantics, running programs, generating specs, and inspecting proofs.

For semantics details and specialized workflows, see [Further Reading](#further-reading).

## Quick Start

### Prerequisites

- [Python](https://www.python.org/) `>= 3.10`
- [`uv`](https://docs.astral.sh/uv/)
- [`pip`](https://pip.pypa.io/) `>= 20.0.2`
- [`gcc`](https://gcc.gnu.org/) `>= 11.4.0`
- [Rust](https://rustup.rs/) via `rustup`
- [K Framework](https://github.com/runtimeverification/k?tab=readme-ov-file#quick-start), using the version pinned in [`deps/k_release`](deps/k_release)

### Clone and set up

```bash
git clone --recurse-submodules https://github.com/runtimeverification/mir-semantics.git
cd mir-semantics

# If you cloned without --recurse-submodules:
git submodule update --init --recursive
```

### Build

The pinned Rust toolchain and components are declared in [`rust-toolchain.toml`](rust-toolchain.toml) and installed automatically by `rustup` on first use.

```bash
# Build K semantics definitions (required for kmir)
make build

# Build stable-mir-json (required for SMIR generation, integration tests)
make stable-mir-json
```

`uv` will create and use the Python environment for the `kmir` project automatically.

### Verify the setup

```bash
# Just kmir
uv --project kmir run kmir --help

# Full contributor check
make smir-parse-tests
```

## Common Workflows

### Task-to-command map

| Task | Command | Notes |
| --- | --- | --- |
| Build the semantics | `make build` | Requires K and the Python prerequisites. |
| Build `stable-mir-json` in-tree | `make stable-mir-json` | Requires initialized submodules and the pinned Rust nightly. |
| Run unit tests | `make test-unit` | Python-only tests under `kmir/src/tests/unit`. |
| Run integration tests | `make test-integration` | Depends on `stable-mir-json` and `build`. |
| Check Stable MIR parsing | `make smir-parse-tests` | Compiles Rust test programs to SMIR JSON and parses them with `kmir`. |

`make test-integration` already depends on `make stable-mir-json` and `make build`, so it is the full contributor path for integration coverage.

## Using `kmir`

Every subcommand supports `--help` for the full option list.

| Command | Purpose |
| --- | --- |
| `kmir run` | Execute a Rust program from SMIR JSON |
| `kmir prove` | Prove properties of a Rust source file (recommended entry point) |
| `kmir show` | Inspect a proof graph — nodes, deltas, rules, statistics |
| `kmir view` | Interactive proof viewer |
| `kmir prune` | Remove a node (and its subtree) from a proof |
| `kmir section-edge` | Split a proof edge into finer sections |
| `kmir link` | Link multiple SMIR JSON files into one |
| `kmir info` | Show type information from a SMIR JSON file |

### Typical proof workflow

```bash
# 1. Run a proof
uv --project kmir run kmir prove program.rs --proof-dir ./proofs --verbose

# 2. Overview — see all leaves and statistics
uv --project kmir run kmir show proof_id --proof-dir ./proofs --leaves --statistics

# 3. Zoom into specific nodes / transitions
uv --project kmir run kmir show proof_id --proof-dir ./proofs --nodes "4,5" --node-deltas "4:5"

# 4. See which K rules fired on an edge
uv --project kmir run kmir show proof_id --proof-dir ./proofs --rules "4:5"

# 5. Full detail for deep debugging
uv --project kmir run kmir show proof_id --proof-dir ./proofs --nodes "5" \
    --full-printer --no-omit-static-info --no-omit-current-body
```

### Debugging a stuck or failing proof

When a proof does not close, the typical cycle is **inspect → refine → re-prove**:

```bash
# Narrow down where things go wrong — break on every function call
uv --project kmir run kmir prove program.rs --proof-dir ./proofs \
    --break-on-calls --max-depth 200

# Or break only when a specific function is entered
uv --project kmir run kmir prove program.rs --proof-dir ./proofs \
    --break-on-function "my_module::suspect_fn"

# Split a large edge to find the exact divergence point
uv --project kmir run kmir section-edge proof_id "4,5" --proof-dir ./proofs --sections 4

# Prune a bad subtree and re-run
uv --project kmir run kmir prune proof_id 5 --proof-dir ./proofs
uv --project kmir run kmir prove program.rs --proof-dir ./proofs

# Export a proof subgraph as a reusable K module
uv --project kmir run kmir show proof_id --proof-dir ./proofs --to-module lemma.json --minimize-proof
# then re-prove with the lemma
uv --project kmir run kmir prove program.rs --proof-dir ./proofs --add-module lemma.json
```

Other useful `prove` break flags: `--break-every-step`, `--break-every-terminator`, `--break-on-thunk`, `--terminate-on-thunk`.

### Generate Stable MIR JSON manually

After `make stable-mir-json`:

```bash
# Single file
deps/.stable-mir-json/debug.sh -Zno-codegen your_file.rs

# Cargo project
RUSTC=deps/.stable-mir-json/debug.sh cargo build

# Convenience script (also supports png/pdf/dot visualization)
./scripts/generate-smir-json.sh <rust-file> <output-dir> [png|pdf|dot]
```

## Troubleshooting

- **Rust toolchain errors**: The toolchain is declared in [`rust-toolchain.toml`](rust-toolchain.toml) and should install automatically on first use. If not, run `rustup toolchain install nightly-2024-11-29 --component llvm-tools --component rustc-dev --component rust-src`.
- **`deps/stable-mir-json` is missing**: Run `git submodule update --init --recursive`.
- **Not sure which `make` target to run**: `make build` for basic `kmir`; add `make stable-mir-json` for SMIR generation; `make test-integration` for the full suite.

## Further Reading

- [docs/semantics-of-mir.md](docs/semantics-of-mir.md)
- [docs/example-mir-execution-flow.md](docs/example-mir-execution-flow.md)
- [docs/dev/adding-intrinsics.md](docs/dev/adding-intrinsics.md)
- [docs/feature-checklist.md](docs/feature-checklist.md)
- [Stable-MIR-JSON repository](https://github.com/runtimeverification/stable-mir-json/)

## Supporters

KMIR / mir-semantics is supported by funding from:
- [Polkadot Open Gov](https://polkadot.subsquare.io/referenda/749)
- Solana
