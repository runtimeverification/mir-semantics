# MIR Semantics

In this repository, we provide a model of the semantics of Rust's Stable MIR in K to enable symbolic execution of Rust programs and proofs of program properties.

Also included is the `kmir` tool, a python script that acts as a front-end to the semantics.


## For Developers

### KMIR Setup

Pre-requisites: `python >= 3.10`, `pip >= 20.0.2`, `uv >= 0.7.11`, `gcc >= 11.4.0`, `cargo == nightly-2024-11-29`, `k >= v7.1.205`. To install K, follow the steps available in [K's Quick Start instructions](https://github.com/runtimeverification/k?tab=readme-ov-file#quick-start). 

```bash
make build
```

Use `make` to run common tasks (see the [Makefile](Makefile) for a complete list of available targets).

For interactive use, first sync the environment with `uv --directory kmir sync`, then either:
- Run Python directly: `uv --directory kmir run python`
- Activate the virtual environment: `source kmir/.venv/bin/activate` (on Unix/macOS) or `kmir\.venv\Scripts\activate` (on Windows)
- Or directly run commands from `mir-semantics` root: `uv --directory kmir run kmir <COMMAND>`

### Stable-MIR-JSON Setup

To interact with some of KMIR functionalities, it is necessary to provide the tool with a serialized JSON of a Rust program's Stable MIR. To be able to extract these serialized SMIR JSONs, you can use the `Stable-MIR-JSON` tool.

#### Quick Start
```bash
git submodule update --init --recursive
make stable-mir-json
```

#### Generating SMIR JSON Files

After setting up stable-mir-json, you can generate SMIR JSON files from Rust source code:

**Using the stable-mir-json tool directly:**
```bash
# For single files
deps/.stable-mir-json/debug.sh -Zno-codegen your_file.rs

# For cargo projects
RUSTC=deps/.stable-mir-json/debug.sh cargo build
```

**Using the convenience script:**
```bash
# Generate JSON file
./scripts/generate-smir-json.sh your_file.rs .

# Generate with visualization (PNG, PDF, DOT)
./scripts/generate-smir-json.sh your_file.rs . png
./scripts/generate-smir-json.sh your_file.rs . pdf
./scripts/generate-smir-json.sh your_file.rs . dot
```

For more information on testing, installation, and general usage of this tool, please check [Stable-MIR-JSON's repository](https://github.com/runtimeverification/stable-mir-json/).

## Usage

Use `--help` with each command for more details.

### Basic Commands

**`kmir run`** - Execute a Rust program from SMIR JSON or directly from source
```bash
# Run from SMIR JSON file
uv --directory kmir run kmir run --file path/to/program.smir.json

# Run with verbose output
uv --directory kmir run kmir run --file path/to/program.smir.json --verbose
```

**`kmir prove-rs`** - Directly prove properties of Rust source code (recommended)
```bash
# Basic proof
uv --directory kmir run kmir prove-rs path/to/program.rs

# Detailed proof with output
uv --directory kmir run kmir prove-rs path/to/program.rs --verbose --proof-dir ./proof_dir
```

**`kmir gen-spec`** - Generate K specification from SMIR JSON
```bash
uv --directory kmir run kmir gen-spec path/to/program.smir.json --output-file path/to/spec.k
```

**`kmir link`** - Link together multiple SMIR JSON files
```bash
# Link multiple SMIR JSON files into a single output file
uv --directory kmir run kmir link file1.smir.json file2.smir.json file3.smir.json --output-file linked.smir.json

# Use default output filename (linker_output.smir.json)
uv --directory kmir run kmir link file1.smir.json file2.smir.json
```

### Analysis Commands

**`kmir show`** - Display proof information
```bash
uv --directory kmir run kmir show proof_id --proof-dir ./proof_dir
```

**`kmir view`** - Detailed view of proof results
```bash
uv --directory kmir run kmir view proof_id --proof-dir ./proof_dir --verbose
```

**`kmir show-rules`** - Show rules applied between nodes
```bash
uv --directory kmir run kmir show-rules proof_id source_node target_node --proof-dir ./proof_dir
```

### Recommended Workflow

1. **Setup Environment**:
   ```bash
   make stable-mir-json  # Setup stable-mir-json
   make build  # Build K definitions
   ```

2. **Direct Proof** (Recommended):
   ```bash
   uv --directory kmir run kmir prove-rs your_file.rs --verbose --proof-dir ./proof_dir
   ```

3. **View Results**:
   ```bash
   uv --directory kmir run kmir show proof_id --proof-dir ./proof_dir
   uv --directory kmir run kmir view proof_id --proof-dir ./proof_dir --verbose
   ```

4. **Analyze Rules**:
   ```bash
   uv --directory kmir run kmir show-rules proof_id 1 3 --proof-dir ./proof_dir
   ```

### Command Options

Most commands support:
- `--verbose, -v`: Detailed output
- `--debug`: Debug information
- `--proof-dir DIR`: Directory for proof results
- `--max-depth DEPTH`: Maximum execution depth
- `--max-iterations ITERATIONS`: Maximum iterations

For complete options, use `--help` with each command.

### Supporters

KMIR / mir-semantics is supported by funding from the following sources:
- [Polkadot Open Gov](https://polkadot.subsquare.io/referenda/749)
- Solana
