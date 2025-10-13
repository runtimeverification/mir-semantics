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

