# kmir

## Installation

Prerequsites: `python 3.8.*`, `pip >= 20.0.2`, `poetry >= 1.3.2`.

```bash
make build
pip install dist/*.whl
```

## For Developers

### Using the build system

The build system is a mixture of `poetry` + `kbuild` + `make`:
* `poetry` handles Python dependencies, see [pyproject.toml](`pyproject.toml`) for Python-related configuration;
* `kbuild` handles K dependencies and build targets, see [kbuild.toml](`kbuild.toml`);
* `make` ties the two together.

### Working on the Python files

The Python source code of the `kmir` tool and library resides in [`src/`](src). The entry point to the tool is [`src/kmir/__main__.py`](src/kmir/__main__.py).

Use `make` to run common tasks (see the [Makefile](Makefile) for a complete list of available targets).

* `make build`: Build wheel
* `make check`: Check code style
* `make format`: Format code
* `make test-unit`: Run unit tests

For interactive use, spawn a shell with `poetry shell` (after `poetry install`), then run an interpreter.

### Working on the K files

The K source code of the semantics resides in [`k-src`](k-src).

Working on the semantics (targeting the LLVM backend) roughly comprises the following steps:
0. Pick a Mir/Rust program as a running example, or a several of them
1. Modify K files
2. Run `poetry run kbuild kompile llvm` to re-kompile the semantics
3. Run a concrete example with `kmir run` -> goto 1
4. Once happy with the step 3 goes, run a part of the integration tests by calling:
   ```
   TEST_ARGS=`--kbuild-dir ~/.kbuild -k test_handwritten` make test-integration-run
   ```
   Modify the command as necessary to include the tests you want. Use `TEST_ARGS='--kbuild-dir ~/.kbuild'` to use your transient `kbuild` artifacts (the kompiled definition) to avoid rebuilding from scratch.
5. Once happy with the step 4 goes, run the complete integration test suite:
   ```
   make test-integration-run
   ```
   This time, do not include the `--kbuild-dir` option to re-kompile everything in a temporary directory.

### Executing Mir programs with `kmir`

Use the following commands from the `kmir` directory to manually run the Mir files using the generated interpreter.
Use `--output pretty` to see the un-parsed final configuration. Run the handwritten Mir like this:
```
poetry run kmir run --definition-dir $(poetry run kbuild which llvm) --output pretty src/tests/integration/test-data/handwritten-mir/execution/arithm-simple.mir
```

Or a Mir compiled from handwritten Rust:
```
poetry run kmir run --definition-dir $(poetry run kbuild which llvm) --output pretty src/tests/integration/test-data/handwritten-rust/test-binop.mir
```

These commands are verbose. To make them a little less so, you could set an environment variable to store the definition path:
```
export KMIR_DEFINITION=$(poetry run kbuild which llvm)
poetry run kmir run --definition-dir $KMIR_DEFINITION --output pretty src/tests/integration/test-data/handwritten-rust/test-binop.mir
```


To reduce this friction a little, we provide a simple `bash` script [`doit.sh`](doit.sh) that encapsulates the common `kmir` calls.
