KMIR &mdash; the [K](http://github.com/kframework) semantics of [MIR (Mid-level IR of Rust)](https://rustc-dev-guide.rust-lang.org/mir/index.html)
=============================================================

🛠️**Work in progress**🛠️

KMIR defines MIR semantics formally in K and enables the scalable testing and verification of Rust smart contracts and applications.

## Getting Started

-   Install K using `kup`(Recommended) , refer to [K Insallation Guide](https://github.com/runtimeverification/k) for more
-   Clone this repo with `submodule` enabled:  
    - `git clone --recurse-submodules git@github.com:runtimeverification/mir-semantics.git`
    - Or update submodules using: `git submodule update --init --recursive`

Alternatively, you can run the tests inside a Docker container, where `5.5.97` is a targetted K version.
```
$ docker build . --build-arg K_COMMIT=5.5.97 --tag mir-semantics:5.5.97
$ docker run --rm -it -u user -w $(pwd) -v $(pwd):$(pwd):ro mir-semantics:5.5.97 make -C kmir test-integration
```

## Build and Run tests
Detailed instructions with prerequisites [here](https://github.com/runtimeverification/mir-semantics/tree/master/kmir).
```
cd kmir
make build
make test-integration
```
## Test Interpretation
### Parsing test cases
The folder `kmir/src/tests/integration/test-data/parsing/` contains the manually written test cases for inidividual MIR constructs and simple MIR programs.

### The `compiletest-rs` test cases
Submodule [`compiletest-rs`](https://github.com/runtimeverification/mir-semantics-compiletest/tree/9251b00e38504a6f1279b0ca9f81b90b4964080d) 
contains MIR programs emitted from `rustc`'s `ui` test cases. This test suite ensures comprehensive test coverage of MIR syntax.

### Test result interpretation
Running of these test cases are integrated to CI's integration test. 
- The `PASS` indicates a successful parsing;
- The `SKIP` incicates a test cases failed parsing right now. (Goals for next milestone)
> Runing these test cases will all return a `SKIP` result, since evaluation rules for MIR in K is not implemented yet.
