<!-- Instead of rewriting our own feature checklist from scratch, we make a derivative of the
[Verus checklist](https://github.com/verus-lang/verus/blob/main/source/docs/guide/src/features.md)
which is available for use under [MIT](https://github.com/verus-lang/verus/blob/main/LICENSE)
license.
-->

**Last Updated: 2026-06-18**

Status reflects concrete execution against the Rust UI test suite. Many limitations trace back to a
single missing component: an **address model** (a representation of addresses in memory). Types whose
values own heap-allocated data (`Box`, `Vec`, etc.) additionally need dynamic (heap)
allocation of that data, built on the address model. **A _Supported_ label can be followed by an
address-model caveat** (e.g. references work, but not references into heap/static data, which are not modeled yet). Therefore, please read
the *Notes* for a full description of the supported features.
Such dependencies are flagged in bold as **Requires the address model** / **Requires heap allocation**.

## Items
|Feature|Status|Notes|
|-------|------|-----|
|Functions, methods, associated functions|Supported|indirect calls through a stored function pointer: see Function pointer types|
|Associated constants|Supported||
|Structs|Partially supported|construction and field access work; decoding reordered/padded layouts from raw bytes not yet|
|Enums|Partially supported|construction and matching work; decoding with-field / niche-encoded variants from raw bytes not yet|
|Const functions|Supported||
|Async functions|Not supported|desugars to coroutines (also not supported)|
|Macros|N/A (MIR)||
|Type aliases|Supported|resolved before MIR|
|Const items|Supported|value constants work; **Requires the address model** for constants holding references into data (`&str`, `&[T]`)|
|Static items|Not supported|**Requires the address model**|

## Struct/enum definitions
|Feature|Status|Notes|
|-------|------|-----|
|Type parameters|Supported|monomorphized before MIR|
|Where clauses|Supported|resolved at type-check|
|Lifetime parameters|Supported|erased in MIR|
|Const generics|Supported|monomorphized; complex `generic_const_exprs` (unstable) not yet (see `impl` types)|
|Custom discriminants|Supported||
|Public / private fields|N/A (MIR)||

## Expressions and Statements
|Feature|Status|Notes|
|-------|------|-----|
|Variables, assignment, mutable variables|Supported||
|`if`, `else`|Supported||
|Patterns, `match`, `if let`, match guards|Supported|slice rest-patterns (`[head, tail @ ..]`) not yet|
|Block expressions|Supported||
|Items|Supported||
|`loop`, `while`|Supported||
|`for`|Supported|desugars to iterators|
|`?`|Supported||
|Async blocks|Not supported|desugars to coroutines (also not supported)|
|`await`|Not supported|desugars to coroutines (also not supported)|
|Unsafe blocks|Supported||
|`&`|Supported||
|`&mut`, place expressions|Supported||
|`==`, `!=`|Supported||
|Type cast (`as`)|Partially supported|numeric and pointer casts work; **Requires the address model** for integer↔pointer casts; float casts not yet|
|Compound assigments (`+=`, etc.)|Supported||
|Array expressions|Supported|including multi-dimensional|
|Range expressions|Supported||
|Index expressions|Supported|element indexing works; range-indexing into a sub-slice: see Patterns|
|Tuple expressions|Supported||
|Struct/enum constructors|Supported||
|Field access|Supported|union cross-field access: see Unions|
|Function and method calls|Supported|indirect calls through a stored function pointer: see Function pointer types|
|Closures|Supported||
|Labels, break, continue|Supported||
|Return statements|Supported||

## Integer arithmetic
|Feature|Status|Notes|
|-------|------|-----|
|Arithmetic for unsigned|Supported||
|Arithmetic for signed (`+`, `-`, `*`, `/`, `%`)|Supported||
|Bitwise operations (`&`, `\|`, `!`, `>>`, `<<`)|Supported||
|Arch-dependent types (`usize`, `isize`)|Not supported (fixed width)|`usize`/`isize` work as fixed 64-bit|

## Types and standard library functionality
|Feature|Status|Notes|
|-------|------|-----|
|Integer types|Supported||
|`bool`|Supported||
|`char`|Not supported|char values not yet modeled|
|Strings|Not supported|`str` not yet; `String` **Requires heap allocation**|
|`Vec`|Not supported|**Requires heap allocation**|
|`Option` / `Result`|Supported|construction and matching work; decoding niche/with-field variants from raw bytes not yet (see Enums)|
|Floating point|Not supported|float decoding and arithmetic not yet implemented|
|Slices|Partially supported|indexing and `split_at` work; slice rest-patterns and fat-pointer length metadata not yet|
|Arrays|Partially supported|indexing and multi-dimensional arrays work; slice rest-patterns (`[head, tail @ ..]`) not yet|
|Pointers|Partially supported|place-based pointers partly work (some pointer casts still produce thunks and fail); **Requires the address model** for integer↔pointer casts|
|References (`&`)|Supported|references to stack data work; **Requires the address model** for references to constant/static/heap data|
|Mutable references (`&mut`)|Supported|references to stack data work; **Requires the address model** for references to constant/static/heap data|
|Never type (`!`)|Not supported||
|Function pointer types|Partially supported|passing a function or closure as an argument works; calling indirectly through a stored function pointer not yet|
|Closure types|Supported|`dyn Fn` dispatch: see Trait objects|
|Coroutines / generators|Not supported|underlies async|
|Trait objects (`dyn`)|Not supported|needs dynamic dispatch via vtables; `Box<dyn>` also **Requires heap allocation**|
|`impl` types|Partially supported|return-position and argument `impl Trait` work; some opaque-type cases not yet|
|`Cell`, `RefCell`|Partially supported|`Cell` works; `RefCell` (borrow tracking) not yet|
|Iterators|Supported||
|`HashMap`|Not supported|**Requires heap allocation**|
|Smart pointers (`Box`, `Rc`, `Arc`)|Not supported|**Requires heap allocation**|
|`Pin`|Not supported||
|Hardware intrinsics|Partially supported|several implemented; many (including SIMD) not yet|
|Printing, I/O|Not supported||
|Panic-unwinding|Not supported|panics that abort are detected; unwinding / `catch_unwind` not yet|

## Traits
|Feature|Status|Notes|
|-------|------|-----|
|User-defined traits|Supported||
|Default implementations|Supported||
|Trait bounds on trait declarations|Supported||
|Traits with type arguments|Supported||
|Associated types|Supported||
|Generic associated types|Supported||
|Higher-ranked trait bounds|Supported||
|`Clone`|Supported||
|Marker traits (`Copy`)|Supported||
|Marker traits (`Send`, `Sync`)|Not supported|markers erased in MIR; meaningful only with concurrency which is not supported|
|Standard traits (`Hash`, `Debug`)|Not supported|formatting / hashing machinery not implemented|
|User-defined destructors (`Drop`)|Not supported|destructors do not run (Drop is a no-op); control flow continues|
|`Sized` (`size_of`, `align_of`)|Supported|`size_of_val` on unsized types: see Hardware intrinsics|
|`Deref`, `DerefMut`|Partially supported|user `Deref`/`DerefMut` impls work; `Box`/`Rc` deref **Requires heap allocation**|

## Multi-threading
|Feature|Status|Notes|
|-------|------|-----|
|`Mutex`, `RwLock` (from standard library)|Not supported|**Requires heap allocation** and concurrency|
|Verified lock implementations|Not supported||
|Atomics|Not supported||
|`spawn` and `join`|Not supported|no threading model|
|Interior mutability|Partially supported|`Cell` works; `RefCell` not yet (see Cell/RefCell)|

## Unsafe
|Feature|Status|Notes|
|-------|------|-----|
|Raw pointers|Partially supported|place-based pointers partly work (some pointer casts still produce thunks and fail); **Requires the address model** for integer↔pointer casts|
|Transmute|Partially supported|byte / wrapper / enum transmutes work; **Requires the address model** for transmutes involving pointer/address values|
|Unions|Partially supported|reading the field last written works; cross-field type-punning not yet|
|`UnsafeCell`|Not supported|**Requires the address model**: direct use fails on a pointer-alignment check; `Cell`, built on it, works (see Cell/RefCell)|
|FFI / `extern` functions|Not supported|external functions have no MIR body to execute|

## Crates and code organization
|Feature|Status|Notes|
|-------|------|-----|
|Multi-crate projects|Partially supported||
|Verified crate + unverified crates|Not supported||
|Modules|Supported||
|rustdoc|Not supported||

## Methodology and evidence

The statuses above were derived from three sources, cross-checked:

1. A full run of the Rust **UI test suite** under the LLVM (concrete) backend (~2888 tests).
2. The repository's **integration tests**: the curated `prove-rs` suite (each `*-fail.rs` is *expected* to fail), the `decode-value` cases, and `verify-rust-std`.
3. **Targeted checks**: small programs run directly to probe a specific feature.

A feature is only marked **Supported** when it both has a passing test that exercises it *and* no failing
test has it as the **root cause**. Distinguishing "root cause" from "where execution stops" matters: a test
often gets stuck far from the real problem (e.g. an arithmetic test that fails only because it prints its
result). To attribute correctly we **tracked thunks** (when the semantics cannot yet rewrite an evaluation it
records it as a *thunk*, noting where that thunk was created) and traced each failure back to the thunk that
caused it. This allows us to say that a feature works while its nominal-category failures are due to *other*
unsupported features.

In the table below, *Passing* gives tests that exercise the feature and succeed (integration tests are under
`kmir/src/tests/integration/data/`, UI tests under `tests/ui/`). *Failures attributed to* gives, for the
not-fully-passing rows, representative failing tests in the same area with the **other** feature their failure
actually traces to. UI directories are nominal groupings, so a directory rarely passes entirely even when the
named feature works. A few directories do pass entirely, noted as such.

| Row | Status | Passing | Failures attributed to |
|-----|--------|---------|-----------------------|
| Iterators | Supported | `iterator-simple`, `iter_next_1/2/3`, `iter-eq-copied-take-dereftruncate`; `tests/ui/iterators/iter-map-fold-type-length` | `iter-sum-overflow` → panic-unwinding; `iter-count-overflow` → loop-to-2⁶⁴ timeout; `iter-range` → printing |
| Arrays | Partially supported | `array_match`, `array_write`, `array_nest_compare` (nested `[[u16;3];2]`); `tests/ui/array-slice-vec/{array_const_index-2,copy-out-of-array-1}` | own gap: `tests/ui/array-slice-vec/{subslice-patterns-const-eval,vec-matching-fold}` (slice rest-patterns). Other fails → heap (`box-of-array-of-drop-1`) |
| Slices | Partially supported | `slice-split-at` | same slice rest-pattern gap as Arrays |
| `for` / Range / Index / Struct-enum constructors | Supported | `struct`, `enum`; `tests/ui/structs-enums/{class-methods,borrow-tuple-fields}`; `for`/range via `iterator-simple` + targeted `1..5` checks | `tests/ui/structs-enums/class-cast-to-trait` → heap (Vec alloc); `align-struct` → unimplemented `min_align_of_val` intrinsic |
| Type/lifetime/const generics, where clauses | Supported | monomorphized/erased before MIR; 284 generics / 106 lifetimes / 46 const-generics passing UI tests, e.g. `tests/ui/generics/generic-fn-twice`, `tests/ui/lifetimes/issue-84604`, `tests/ui/const-generics/const-arg-in-fn` | `tests/ui/const-generics` fails → heap/transmute and unimplemented `generic_const_exprs` (`OpaqueCast`) |
| Associated constants | Supported | `tests/ui/associated-consts/{assoc-const,associated-const-const-eval}` (19 passing in dir, 1 fail) | `associated-const-in-global-const` → constant-into-allocation (address model) |
| Const functions | Supported | run like normal functions; `tests/ui/const-generics/min_const_generics/const_fn_in_generics`, targeted `const fn` checks |  |
| Type aliases | Supported | resolved before MIR; `tests/ui/type-alias-enum-variants/` (both tests pass) |  |
| Const items | Supported | value constants work (targeted `const C: u32` checks; no dedicated UI dir); constants holding references into data (`&str`, `&[T]`) need the address model |  |
| Function pointer types | Partially supported | fn-item/closure-as-argument: `488-support-function-pointer-calls` | calling indirectly through a stored/cast function pointer not yet (the `tests/ui/` indirect-call failures) |
| `impl` types | Partially supported | `tests/ui/impl-trait/{closure-in-impl-trait-arg,example-st}`, targeted `impl Fn`/`impl Into` | `equality-rpass` → `OpaqueCast`/`Subtype` projection; others → heap/transmute |
| Transmute | Partially supported | `transmute-bytes`, `transmute_transparent_wrapper_up/down`, `transmute-u8-to-enum`; `tests/ui/transmute/` (passes wholesale) | own gap: `transmute-maybe-uninit-fail`; pointer/address-typed transmutes → address model |
| Unions | Partially supported | `tests/ui/union/{union-derive-rpass,union-inherent-method,union-backcomp}` | own gap: `union-pat-refutability`, `union-const-eval-field` (cross-field punning); `union-align` → unimplemented `min_align_of_val` |
| `Cell` / Interior mutability | Partially supported | `Cell`: `interior-mut2` (no dedicated UI dir) | `RefCell`: `interior-mut-fail` (borrow tracking) |
| Raw pointers / Pointers | Partially supported | place-based: `offset_read`, `pointer-cast` | `raw-ptr-cast-fail` → pointer-alignment check / `ptr as usize` (address model) |
| `Sized` (`size_of`, `align_of`) | Supported | `align_and_size` (all integer widths; no dedicated UI dir) |  |
| `Deref`/`DerefMut` | Partially supported | user impls: `tests/ui/autoref-autoderef/autoderef-privacy` | `Box`/`Rc` deref → heap |
| Hardware intrinsics | Partially supported | `intrinsics` (rotate_left, bswap, ctpop, ctlz_nonzero); `tests/ui/intrinsics/{intrinsic-assume,intrinsic-raw_eq-const}` | `const-eval-select-x86_64` → SIMD; `intrinsic-alignment` → unimplemented `pref_align_of` |
| Smart pointers (`Box`/`Rc`/`Arc`) | Not supported |  | `box_heap_alloc-fail` (expected fail) → heap |
| Static items | Not supported |  | `volatile_load_static-fail`, `volatile_store_static-fail` (expected fail) → address model |
| `UnsafeCell` | Not supported |  | `interior-mut3-fail` (expected fail) → pointer-alignment / address model |
| Floating point | Not supported |  | `verify-rust-std/0011-floats-ints` (`to_int_unchecked` parked); no passing float test |
| Enums (decode of with-field/niche variants) | Partially supported | fieldless variants decode fine (`enum-direct-tag-decode`) | `decode-value` SKIP: `enum-1-variant-1-field`, `enum-option-nonzero-none`, … (with-field/niche decode) |
| Strings | Not supported |  | `decode-value` SKIP `str` |
| `char` | Not supported |  | no `char` value representation (decode rule unimplemented); only size/alignment known |
| Coroutines / generators | Not supported |  | `tests/ui/coroutine/` (all 33 fail, e.g. `addassign-yield`) → `aggregateKindCoroutine` unhandled |
| FFI / `extern` functions | Not supported |  | external functions have no MIR body (e.g. `tests/ui/abi/anon-extern-mod`) |
