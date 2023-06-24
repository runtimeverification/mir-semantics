KMIR &mdash; the [K](http://github.com/kframework) semantics of [MIR (Mid-level IR of Rust)](https://rustc-dev-guide.rust-lang.org/mir/index.html)
=============================================================

🛠️**Work in progress**🛠️

KMIR defines MIR semantics formally in K and enables the scalable testing and verification of Rust smart contracts and applications.

## Getting Started

To get the source code of KMIR, clone this repository:
```
$ git clone --recurse-submodules git@github.com:runtimeverification/mir-semantics.git
```

KMIR is built with the K Framework, thus an installation of K is requires to use KMIR. We provide a Docker image for isolated testing, locally and in CI, and also instruction for installing K and KMIR naively for more in-depth exploration and development.

### Running integration tests with `docker`:

- From the root of the repository:
    - Build the docker image (the `./deps/k_release` file pins the K version):
    ```
    $ docker build . --build-arg K_COMMIT=$(cat ./deps/k_release) --tag mir-semantics:$(cat ./deps/k_release)
    ```
    - Run the integration tests in a container:
    ```
    $ docker run --name mir-semantics --rm -it -u user --workdir /home/user mir-semantics:$(cat ./deps/k_release) make -C kmir test-integration
    ```

Note: you may need to run the `docker` commands with `sudo`.

We use a similar workflow in CI actions defined in the `.github/` directory.

### Working on KMIR without `docker`

While the `docker`-based setup is useful for CI and isolated testing, we recommend a native installation of K and other tools for development.

To work on KMIR, the following software is needed:

- The K Framework. See the [K Installation Guide](https://github.com/runtimeverification/k).
- The `poetry` tool to build and manage the Python code. See the [Poetry Installation Guide](https://python-poetry.org/docs/#installation).
- Optionally, the `rustc` Rust compiler to compiler Rust code to MIR. See the [Rust Installation Guide](https://doc.rust-lang.org/book/ch01-01-installation.html)

The KMIR project comprises two major components:
- The K Semantics of MIR, which defines an operational semantics of MIR as rewrite rules in the K Framework. See the `kmir/k-src` for the K files.
- The `kmir` command-line tool and Python library. `kmir` is a Python package that leverages the [`pyk`](https://github.com/runtimeverification/pyk) library to provide a Python interface for the K semantics. While the K semantics can be also used directly, the `kmir` tool makes it more accessible for people not familiar with K. See the `kmir/README.md` for instruction on how to use `kmir` and the available CLI commands.

## KMIR Integration Test Suite

- Parsing test cases
    The folder `kmir/src/tests/integration/test-data/parsing/` contains the manually written test cases for inidividual MIR constructs and simple MIR programs.
- The `compiletest-rs` test cases Submodule [`compiletest-rs`](https://github.com/runtimeverification/mir-semantics-compiletest/tree/9251b00e38504a6f1279b0ca9f81b90b4964080d) contains MIR programs emitted from `rustc`'s `ui` test cases. This test suite ensures comprehensive test coverage of MIR syntax.

- Test result interpretation
    - The `PASS` indicates a successful parsing;
    - The `SKIP` incicates a test cases failed parsing right now. (Goals for next milestone)
    - Executing these test cases should aslo return a `SKIP` result, since evaluation rules for MIR in K is not implemented yet.
