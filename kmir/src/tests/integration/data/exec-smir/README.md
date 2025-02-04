Small tests for MIR execution
-----------------------------

The tests below this directory are intended to be run with `kmir run`, comparing the pretty-printed output to an expectation file.

# To add a new test

* Write a Rust test program `NAME.rs`
* Generate stable-mir JSON `NAME.smir.json` for the test program (using `deps/stable-mir-pretty`)
* run the program once to generate the expected output state
  ```
  /mir-semantics $ poetry -C kmir run -- kmir run path/to/NAME.smir.json > <path>/<to>/<NAME>.run.state
  ```
* check that the output is as expected
* add test to `EXEC_DATA` array in `kmir/src/tests/integration/test_integration.py`
* Several tests can be run from the same `NAME.smir.json` by varying the `--depth` parameter.


Ideally, we should also keep the original `NAME.rs` program so we can later update the tests when/if the JSON format changes.
