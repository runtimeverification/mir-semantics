Compiling a Rust program via SMIR JSON to a K module
============================

To avoid fattening the configuration beyond the size manageable for the symbolic backend,
static elements of the configuration (function table, types table, allocs table, adt table)
are translated to K functions in a dedicated module. 
This module is then imported into the KMIR semantics to extend the function equations provided in the semantics.

Note: no need to _extend_, instead we can just provide that module for import.
Requires standard name and location, complicates debugging as we don't know which program we were dealing with.

# Adapting the semantics

* Declare functions to look up static data.
  - Functions declared total, return dummy values in `[owise]` rules for now (HACK).
  - Functions are currently declared in `value.md` module, could have their own module.
  - TODO inconsistent naming
* All uses of static data cells in the semantics replaced by function calls

# Generating a module with the declared functions for a particular program

* Python code `SMIR -> K Module (as Text)`
* imports `VALUE-SYNTAX` (`value.md`) to bring function declaration into scope
* imports `KMIR` to have semantics in scope 

* Four groups of equations
    1. `lookupFunction : Ty -> MonoItemKind`
        - depends on `MONO` (`mono.md`), already present via `RT-VALUE-SYNTAX`
        - contains equations `lookupFunction(ty(N)) => Item`
          - item with symbol_name from `functions[N]`
          - add negative `N` for all items not present in `functions`
        - most Python code exists in `kmir.py::_make_function_map`
            but needs to be copied and modified to make function equations instead of a K `Map`
    2. `lookupAlloc : AllocId -> Value`
        - depends on `RT-DECODING` (`decoding.md`)
        - contains equations `lookupAlloc(ID) => decodeAlloc(ID, TY, ALLOC)[ID]`
          - TODO remove the `Map` return
          - using data from `allocs` (each `AllocInfo(ID, TY, ALLOC)`)
        - we should probably decode in python later?
    3. `lookupTy : Ty -> TypeInfo`
        - depends on `TYPES` (`ty.md`), already present via `RT-VALUE-SYNTAX`
        - contains equations `lookupTy(T) => typeInfo`
            - using data from `types` (each `[T, TypeInfo]`)
        - most python code exists in `kmir.py::_make_type_and_adt_maps`
    4. `lookupAdtTy : AdtDef -> Ty`
        - depends on `TYPES` (`ty.md`), already present
        - most python code exists in `kmir.py::_make_type_and_adt_maps`

# Compiling the module together with the semantics

The generated module becomes the main module to run `kompile` calls on
- three compilations: llvm, llvm-library, haskell

The compiled artefacts should be what the `KMIR` class uses (`definition_dir`).

That means, the module generation and compilation happens when creating the `KMIR` object.
Module and compilation results should be cached (can be omitted in a prototype, recompiling every time using temp files).

# Changes to running and proving

To run a program/function or prove a property, we still generate a call configuration
but the configuration does not have any static fields any more.
The configuration is executed with the compiled module.

# Obstacles

1. LLVM backend is confused about symbol versions when an `@` char is in a string or binary data (`\x40h`).
   This was caused by the LLVM backend using the literal kore string as a symbol name. Fixed in llvm backend, open PR.
2. Compilation fails because of "long" lists (>100 elements) causing problems in the rule parser.
   Work-arounds considered: 
   - generate kore instead , and insert it into the `definition.kore`
     - need to do this manually as there are no helper functions to make `kore` rules directly. 
   - generate `kast` syntax and splice into the K code. 
     - need to extend `pyk` with a `kast` pretty-printer. The `kast` format specification is somewhat tricky and incomplete, as I was told.
   Work-around 1 appears to work, code developed on new branch extending the other.
   

# Technical work to prepare the change

## Integration tests
- [ ] `test_decode_value`: need to replace type map by definition contents (non-python tests only)
  - pre-compile an LLVM interpreter with the types fixed to a standard table (covering all test cases)
  - alternative is compiling once per test, bad.
- [ ] `exec_smir`: needs an implementation of `kmir run` for concrete execution, LLVM and Haskell
  - KMIR.run_smir should just be a static method, preparing the definition beforehand
  - BTW the _binary_ format is the problem for `kmir run` with `--backend haskell`
- [ ] `prove_rs`:
  - [X] turned `KMIR.prove_rs` into a static method, preparing the definition beforehand
  - [ ] proof failures: 
    ```
    FAILED test_prove_termination[Ref-weirdRefs] - assert False
    FAILED test_prove_termination[Array-indexing] - assert False
    FAILED test_prove_termination[Array-index-writes] - assert False
    FAILED test_prove_termination[Array-inlined] - assert False
    FAILED test_prove_termination[Alloc-array-const-compare] - assert False
    FAILED test_prove_termination[niche-enum] - assert False
    FAILED test_prove_termination[main-a-b-c] - assert False
    FAILED test_prove_termination[assign-cast] - assert False
    FAILED test_prove_termination[struct-field-update] - assert False
    FAILED test_prove_termination[arithmetic] - assert False
    FAILED test_prove_termination[arithmetic-unchecked] - assert False
    FAILED test_prove_termination[unary] - assert False
    FAILED test_prove_termination[Ref-simple] - assert False
    FAILED test_prove_termination[Ref-refAsArg] - assert False
    FAILED test_prove_termination[Ref-doubleRef] - assert False
    ```
    - `test_prove_termination` for all failing tests.
    - uses `gen-spec` and `prove-raw`
    - should instead use `prove-rs --smir`

  - [ ] compilation failures (non-deterministic):
    ```
    FAILED test_prove_rs[double-ref-deref] - subprocess.CalledProcessError: Command '['llvm-kompile', 'out-kore/llvm-library/definition.kore', 'out-kore/llvm-library/dt', 'c', '-O2', '--', '-o', PosixPath('out-kore/llvm-library/interpreter')]'...
    FAILED test_prove_rs[array_nest_compare] - subprocess.CalledProcessError: Command '['llvm-kompile', 'out-kore/llvm-library/definition.kore', 'out-kore/llvm-library/dt', 'c', '-O2', '--', '-o', PosixPath('out-kore/llvm-library/interpreter')]'...
    FAILED test_prove_rs[branch-negative] - subprocess.CalledProcessError: Command '['llvm-kompile', 'out-kore/llvm-library/definition.kore', 'out-kore/llvm-library/dt', 'c', '-O2', '--', '-o', PosixPath('out-kore/llvm-library/interpreter')]'...
    FAILED test_prove_rs[bitwise-not-shift] - subprocess.CalledProcessError: Command '['llvm-kompile', 'out-kore/llvm-library/definition.kore', 'out-kore/llvm-library/dt', 'c', '-O2', '--', '-o', PosixPath('out-kore/llvm-library/interpreter')]'...
    FAILED test_prove_rs[pointer-cast] - subprocess.CalledProcessError: Command '['llvm-kompile', 'out-kore/llvm-library/definition.kore', 'out-kore/llvm-library/dt', 'c', '-O2', '--', '-o', PosixPath('out-kore/llvm-library/interpreter')]'...
    ```
    - caused by concurrent access to the same files. Need to compile into temp directory or proof-dir
  - [ ] Unexpected output: Probably always an additional step to an unknown function
    ```
    FAILED kmir/src/tests/integration/test_cli.py::test_cli_show_statistics_and_leaves - AssertionError: The actual output does not match the expected output:
    FAILED test_prove_rs[symbolic-structs-fail] - AssertionError: The actual output does not match the expected output:
    FAILED test_crate_examples[single-lib] - AssertionError: The actual output does not match the expected output:
    FAILED test_prove_rs[symbolic-args-fail] - AssertionError: The actual output does not match the expected output:
    FAILED test_prove_rs[pointer-cast-length-test-fail] - AssertionError: The actual output does not match the expected output:
    ```
    - could extend the function lookup and provide the symbol name for functions not present in the items table.
    - or just leave things as they are, not much difference to before (getting stuck one step later now)
- [ ] `test_prove`: single test with a checked-in spec file. Delete this test!

1. use temp directory or proof directory for prove-rs DONE
2. do not copy the bin file for HS backend DONE
3. implement LLVM backend compilation for concrete execution DONE
4. implement KMIR.run_rs static (with the above)
   - or rather factor out the compilation method and revert prove_rs change
5. delete `test_prove` test
6. re-test (without `test_decode_value`)
