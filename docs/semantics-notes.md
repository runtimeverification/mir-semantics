We recommend reading through the [MIR construction](https://rustc-dev-guide.rust-lang.org/mir/construction.html) section of the `rustc` dev guide. It provides good insight on what some Mir constructs mean.

Another useful resource if the `rustc` dev guide [Glossary](https://rustc-dev-guide.rust-lang.org/appendix/glossary.html).

We keep an assortment of notes we see relevant to the sematnics below:

Note on `_0`
-----------

It looks line the location `_0` is generated automatically and we do not need the sematics to generate it.
Rather, we should fail with a meaningful error if it's missing.

Macros
------

The Rust macros get compiled to quite a lot of code because Mir has no explicit macros. We need to figure out their semantics.

Promoted
--------

Explanation of what `promoted` is. See also the [docs](https://github.com/rust-lang/const-eval/blob/33053bb2c9a0c6a17acd3116dd47bbb360e060db/promotion.md) of `const-eval`:

> Constants extracted from a function and lifted to static scope

> "Promotion" is the act of splicing a part of a MIR computation out into a separate self-contained MIR body which is evaluated at compile-time like a constant.



Looks like the `promoted` "functions" correspond to constants that occur in the program.
For example, if the program prints a constant with the `pirnt!` macro, the generated Mir will contain the promoted constants for
the printed number and the argument formatter. i.e.:

```rust
fn main() {
    print!("{}", 42);
}
```

generates the following Mir (redacted):

```mir
// that's the constant we're printing
promoted[0] in main: &i32 = {
    let mut _0: &i32;
    let mut _1: i32;

    bb0: {
        _1 = const 42_i32;
        _0 = &_1;
        return;
    }
}

// that's the formatter string, the first argument of `print!`
promoted[1] in main: &[&str; 1] = {
    let mut _0: &[&str; 1];
    let mut _1: [&str; 1];

    bb0: {
        _1 = [const ""];
        _0 = &_1;
        return;
    }
}
```

TODO: how are promoted constants referred to?

Looks like the promoted constants are refereed to by their **index**. I.e. the Nth `const` grabs the Nth promoted, i.e. `promoted[N]`. For example:

```
fn main() -> () {
    ...
    let _1: i32;
    let mut _2: &[&str; 1];

    bb0: {
        _1 = const _; // referes to promoted [0]
        _2 = const _; // referes to promoted [1]
```

Duplicate literals seems to produce duplicate promoted constants.

RANDOM REFERENCES
-----------------

https://github.com/rust-lang/miri/blob/master/src/eval.rs#L84
https://github.com/rust-lang/miri/blob/master/src/machine.rs#L349

https://doc.rust-lang.org/beta/nightly-rustc/miri/index.html
