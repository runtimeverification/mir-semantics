<!-- Instead of rewriting our own feature checklist from scratch, we make a derivative of the
[Verus checklist](https://github.com/verus-lang/verus/blob/main/source/docs/guide/src/features.md)
which is available for use under [MIT](https://github.com/verus-lang/verus/blob/main/LICENSE)
license.
-->

**Last Updated: 2025-04-10**

## Items
|Feature|Status|
|-------|------|
|Functions, methods, associated functions|Supported|
|Associated constants|Not supported|
|Structs|Partially supported|
|Enums|Partially supported|
|Const functions|Not supported|
|Async functions|Not supported|
|Macros|Not supported|
|Type aliases|Not supported
|Const items|Not supported|
|Static items|Not supported|

## Struct/enum definitions
|Feature|Status|
|-------|------|
|Type parameters|Not supported|
|Where clauses|Not supported|
|Lifetime parameters|Not supported|
|Const generics|Not supported|
|Custom discriminants| Supported|
|Public / private fields|N/A (MIR)|

## Expressions and Statements
|Feature|Status|
|-------|------|
|Variables, assignment, mutable variables|Supported|
|`if`, `else`|Supported|
|Patterns, `match`, `if let`, match guards|Supported|
|Block expressions|Supported|
|Items|Supported|
|`loop`, `while`|Supported|
|`for`|Not supported (`Range` not supported)|
|`?`|Supported|
|Async blocks|Not supported|
|`await`|Not supported|
|Unsafe blocks|Supported|
|`&`|Supported|
|`&mut`, place expressions|Supported|
|`==`, `!=`|Supported|
|Type cast (`as`)|Partially supported|
|Compound assigments (`+=`, etc.)|Supported|
|Array expressions|Not supported|
|Range expressions|Not supported|
|Index expressions|Not supported (Arrays not supported)|
|Tuple expressions|Supported|
|Struct/enum constructors|Not supported|
|Field access|Supported|
|Function and method calls|Supported|
|Closures|Supported|
|Labels, break, continue|Supported|
|Return statements|Supported|

## Integer arithmetic
|Feature|Status|
|-------|------|
|Arithmetic for unsigned|Supported|
|Arithmetic for signed (`+`, `-`, `*`, `/`, `%`)|Supported|
|Bitwise operations (`&`, `\|`, `!`, `>>`, `<<`)|Supported|
|Arch-dependent types (`usize`, `isize`)|Not supported (fixed width) |

## Types and standard library functionality
|Feature|Status|
|-------|------|
|Integer types|Supported|
|`bool`|Supported|
|Strings|Not supported|
|`Vec`|Not supported|
|`Option` / `Result`|Supported|
|Floating point|Not supported|
|Slices|Not supported|
|Arrays|Not supported|
|Pointers|Not supported|
|References (`&`)|Supported|
|Mutable references (`&mut`)|Supported|
|Never type (`!`)|Not supported|
|Function pointer types|Not supported|
|Closure types|Supported|
|Trait objects (`dyn`)|Not supported|
|`impl` types|Not supported|
|`Cell`, `RefCell`|Not supported|
|Iterators|Not supported|
|`HashMap`|Not supported|
|Smart pointers (`Box`, `Rc`, `Arc`)|Not supported|
|`Pin`|Not supported|
|Hardware intrinsics|Not supported|
|Printing, I/O|Not supported|
|Panic-unwinding|Not supported|

## Traits
|Feature|Status|
|-------|------|
|User-defined traits|Supported|
|Default implementations|Supported|
|Trait bounds on trait declarations|Supported|
|Traits with type arguments|Supported|
|Associated types|Supported|
|Generic associated types|Supported|
|Higher-ranked trait bounds|Supported|
|`Clone`|Supported|
|Marker traits (`Copy`)|Supported|
|Marker traits (`Send`, `Sync`)|Not supported|
|Standard traits (`Hash`, `Debug`)|Not supported|
|User-defined destructors (`Drop`)|Not supported|
|`Sized` (`size_of`, `align_of`)|Not supported|
|`Deref`, `DerefMut`|Not supported|

## Multi-threading
|Feature|Status|
|-------|------|
|`Mutex`, `RwLock` (from standard library)|Not supported
|Verified lock implementations|Not supported
|Atomics|Not supported|
|`spawn` and `join`|Not supported|
|Interior mutability|Not supported|

## Unsafe
|Feature|Status|
|-------|------|
|Raw pointers|Not supported|
|Transmute|Not supported|
|Unions|Not supported|
|`UnsafeCell`|Not supported|

## Crates and code organization
|Feature|Status|
|-------|------|
|Multi-crate projects|Partially supported|
|Verified crate + unverified crates|Not supported|
|Modules|Supported|
|rustdoc|Not supported|