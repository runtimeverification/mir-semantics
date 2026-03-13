# verify-rust-std challenges

Test harnesses for verify-rust-std ([docs](https://model-checking.github.io/verify-rust-std/) / [github](https://github.com/model-checking/verify-rust-std/)) challenges. Each subdirectory corresponds to a challenge and contains a README.md on progress.

All tests are run with `--terminate-on-thunk`, so unresolved symbolic expressions (e.g. from unchecked operations with unmet preconditions) cause the proof to terminate rather than propagate. This means `-fail` tests detect UB by the prover being unable to resolve the unchecked operation on the violating path.
