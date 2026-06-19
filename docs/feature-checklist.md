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
|Const generics|Supported|monomorphized; complex `generic_const_exprs` (unstable) not yet — see `impl` types|
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
|`Option` / `Result`|Supported|construction and matching work; decoding niche/with-field variants from raw bytes not yet — see Enums|
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
|Interior mutability|Partially supported|`Cell` works; `RefCell` not yet — see Cell/RefCell|

## Unsafe
|Feature|Status|Notes|
|-------|------|-----|
|Raw pointers|Partially supported|place-based pointers partly work (some pointer casts still produce thunks and fail); **Requires the address model** for integer↔pointer casts|
|Transmute|Partially supported|byte / wrapper / enum transmutes work; **Requires the address model** for transmutes involving pointer/address values|
|Unions|Partially supported|reading the field last written works; cross-field type-punning not yet|
|`UnsafeCell`|Not supported|**Requires the address model** — direct use fails on a pointer-alignment check; `Cell`, built on it, works — see Cell/RefCell|
|FFI / `extern` functions|Not supported|external functions have no MIR body to execute|

## Crates and code organization
|Feature|Status|Notes|
|-------|------|-----|
|Multi-crate projects|Partially supported||
|Verified crate + unverified crates|Not supported||
|Modules|Supported||
|rustdoc|Not supported||
