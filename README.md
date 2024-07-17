# MIR Semantics

In this repository, we provide a model of Rust MIR in K.

NOTE: This project is currently under reconstruction with changes and work outlined in [Polkadot Referendum #749](https://polkadot.subsquare.io/referenda/749). Some features you may be familiar with (concrete execution and symbolic execution) are currently removed while project foundations are improved.

Currently the project is working to stablise serialised output of stable MIR (see our current [Rust PR](https://github.com/rust-lang/rust/pull/126963)), and develop the semantics for this output. 

If you would like to try a legacy version of the project, [this blog post](https://runtimeverification.com/blog/introducing-kmir) has a tutorial to get started with. However it is important to install a legacy version for this to work, and so when the tutorial prompts to install the latest version of KMIR with `kup install kmir`, this should be replaced instead with `kup install kmir --version v0.2.21`

## Installation

Prerequsites: `python >= 3.10`, `pip >= 20.0.2`, `poetry >= 1.3.2`.

```bash
make build
pip install dist/*.whl
```


## For Developers

Use `make` to run common tasks (see the [Makefile](Makefile) for a complete list of available targets).

* `make build`: Build wheel

For interactive use, spawn a shell with `poetry -C kmir/ shell` (after `poetry -C kmir/ install`), then run an interpreter.

