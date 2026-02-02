# MIR Semantics

In this repository, we provide a model of the semantics of Rust's Stable MIR in K to enable symbolic execution of Rust programs and proofs of program properties.

Also included is the `kmir` tool, a python script that acts as a front-end to the semantics.


## For Developers

### KMIR Setup

Pre-requisites:
- `python >= 3.10`
- [`uv`](https://docs.astral.sh/uv/)
- `pip >= 20.0.2`
- `gcc >= 11.4.0`
- `cargo == nightly-2024-11-29`
- K. The required K version is specified in `deps/k_release`. To install K, follow the steps available in [K's Quick Start instructions](https://github.com/runtimeverification/k?tab=readme-ov-file#quick-start).

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
uv --project kmir run kmir run --file path/to/program.smir.json

# Run with verbose output
uv --project kmir run kmir run --file path/to/program.smir.json --verbose
```

**`kmir prove-rs`** - Directly prove properties of Rust source code (recommended)
```bash
# Basic proof
uv --project kmir run kmir prove-rs path/to/program.rs

# Detailed proof with output
uv --project kmir run kmir prove-rs path/to/program.rs --verbose --proof-dir ./proof_dir
```

**`kmir gen-spec`** - Generate K specification from SMIR JSON
```bash
uv --project kmir run kmir gen-spec path/to/program.smir.json --output-file path/to/spec.k
```

**`kmir link`** - Link together multiple SMIR JSON files
```bash
# Link multiple SMIR JSON files into a single output file
uv --project kmir run kmir link file1.smir.json file2.smir.json file3.smir.json --output-file linked.smir.json

# Use default output filename (linker_output.smir.json)
uv --project kmir run kmir link file1.smir.json file2.smir.json
```

**`kmir info`** - Inspect SMIR JSON metadata (currently: types)
```bash
# Show information about specific type IDs in a SMIR JSON
uv --project kmir run kmir info path/to/program.smir.json --types "1,2,3"

# Notes
# - The --types option accepts a comma-separated list of numeric Stable MIR type IDs.
# - Output format: one line per requested type, e.g.:
#   Type Ty(1): Int(....)
#   Type Ty(2): StructT(name=..., adt_def=..., fields=[...])
# - If --types is omitted, the command currently produces no output.
```

### Analysis Commands

**`kmir show`** - Display proof information with advanced filtering options
```bash
# Basic usage
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir

# Show specific nodes only
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --nodes "1,2,3"

# Show node deltas (transitions between specific nodes)
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --node-deltas "1:2,3:4"

# Show additional deltas after the main output, and also print rules for those edges
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --node-deltas "1:2" --node-deltas-pro "3:4"

# Display full node information (default is compact)
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --full-printer

# Show static information cells (functions, types, etc.)
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --no-omit-static-info

# Show current body cell content
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --no-omit-current-body

# Omit specific cells from output
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --omit-cells "cell1,cell2"

# Combine multiple options for detailed analysis
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --full-printer --no-omit-static-info --nodes "1,2" --verbose
```

**`kmir view`** - Detailed view of proof results
```bash
uv --project kmir run kmir view proof_id --proof-dir ./proof_dir --verbose
```

**Rules within `kmir show`** - Show rules applied between nodes
```bash
uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --rules "SOURCE:TARGET[,SOURCE:TARGET...]"
```

### Recommended Workflow

1. **Setup Environment**:
   ```bash
   make stable-mir-json  # Setup stable-mir-json
   make build  # Build K definitions
   ```

2. **Direct Proof** (Recommended):
   ```bash
   uv --project kmir run kmir prove-rs your_file.rs --verbose --proof-dir ./proof_dir
   ```

3. **View Results**:
   ```bash
   # Quick overview (compact format, static info hidden)
   uv --project kmir run kmir show proof_id --proof-dir ./proof_dir
   
   # Detailed analysis with full information
   uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --full-printer --no-omit-static-info
   
   # Focus on specific nodes
   uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --nodes "1,2,3"
   
   # Interactive view
   uv --project kmir run kmir view proof_id --proof-dir ./proof_dir --verbose
   ```

4. **Analyze Rules**:
   ```bash
   uv --project kmir run kmir show proof_id --proof-dir ./proof_dir --rules "1:3"
   ```

### Advanced Show Usage Examples

**Debugging workflow:**
```bash
# 1. Start with a quick overview
uv --project kmir run kmir show my_proof --proof-dir ./proofs

# 2. Focus on problematic nodes (e.g., nodes 5, 6, 7)
uv --project kmir run kmir show my_proof --proof-dir ./proofs --nodes "5,6,7"

# 3. Examine transitions between specific nodes
uv --project kmir run kmir show my_proof --proof-dir ./proofs --node-deltas "5:6,6:7"

# 4. Get full details for deep debugging
uv --project kmir run kmir show my_proof --proof-dir ./proofs --nodes "6" --full-printer --no-omit-static-info --no-omit-current-body
```

**Performance analysis:**
```bash
# Hide verbose cells but show execution flow
uv --project kmir run kmir show my_proof --proof-dir ./proofs --omit-cells "locals,heap" --verbose

# Focus on function calls and type information
uv --project kmir run kmir show my_proof --proof-dir ./proofs --no-omit-static-info --omit-cells "currentBody"
```

### Command Options

Most commands support:
- `--verbose, -v`: Detailed output
- `--debug`: Debug information
- `--proof-dir DIR`: Directory for proof results
- `--max-depth DEPTH`: Maximum execution depth
- `--max-iterations ITERATIONS`: Maximum iterations

**`kmir show` specific options:**
- `--nodes NODES`: Comma separated list of node IDs to show (e.g., "1,2,3")
- `--node-deltas DELTAS`: Comma separated list of node deltas in format "source:target" (e.g., "1:2,3:4")
- `--node-deltas-pro DELTAS`: Additional node deltas (same format as `--node-deltas`). Equivalent to "print the corresponding deltas again, and automatically print the rules for these edges".
- `--rules EDGES`: Comma separated list of edges in format "source:target". Prints rules for each edge in Markdown link format `[label](file:///abs/path#LstartLine)` when available
- `--omit-cells CELLS`: Comma separated list of cell names to omit from output
- `--full-printer`: Display the full node in output (default is compact)
- `--no-omit-static-info`: Display static information cells (functions, start-symbol, types, adt-to-ty)
- `--no-omit-current-body`: Display the `<currentBody>` cell completely
- `--smir-info SMIR_INFO`: Path to SMIR JSON file to improve debug messaging

For complete options, use `--help` with each command.

### Supporters

KMIR / mir-semantics is supported by funding from the following sources:
- [Polkadot Open Gov](https://polkadot.subsquare.io/referenda/749)
- Solana
