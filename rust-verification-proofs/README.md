# Formal Rust Code Verification Using KMIR  

This subrepository contains a collection of programs and specifications that aim to illustrate how KMIR can be used to validate the properties of Rust programs and the Rust language itself. The code made available in this repository was developed taking as references the challenges present on the [Verify Rust Standard Library Effort](https://model-checking.github.io/verify-rust-std/intro.html).

## Table of Contents


- [Project Setup](#project-setup)
- [Proof 1: Proving a Maximum Finding Function That only Uses `lower-than (<)`](#proof-1-proving-a-maximum-finding-function-that-only-uses-lower-than)
- [Proof 2: Proving Unsafe Arithmetic Operations](#proof-2-proving-unsafe-arithmetic-operations)

## Project Setup

In order to run and explore the proofs elaborated here, make sure that KMIR can be locally executed in your machine following the instructions available in [this repository's README file](https://github.com/runtimeverification/mir-semantics/tree/sample-challenge-11-proofs).

[Be sure to have Rust installed](https://www.rust-lang.org/tools/install) in your machine, have the specific components and toolchain necessary to run KMIR. To guarantee it, with `rustup` installed, run the following commands: 

```bash
rustup component add rust-src rustc-dev llvm-tools-preview
rustup toolchain install nightly-2024-11-29
rustup default nightly-2024-11-29
```

**(Optional)** Additionally, if you would like to build your own code specifications to be proven with KMIR, install the [Rust Stable MIR Pretty Printing](https://github.com/runtimeverification/stable-mir-json/tree/20820cc6abd8fd22769931a3f8754ee35ab24c05) tool. It won't be necessary to install it if you'd like to understand how KMIR works and to execute its proofs, but it is needed currently to help us traverse program states, as seen in the [steps needed to achieve Proof 1's specification](https://github.com/runtimeverification/mir-semantics/tree/sample-challenge-11-proofs/rust-verification-proofs/maximum-proof). To install the Rust Stable MIR Pretty Printing tool, in the root of this project, run:

```bash
git submodule update --init --recursive
make stable-mir-json
```

The usage of this tool will be abstracted in the future, removing the need to construct claims manually.

## Proof 1: Proving a Maximum Finding Function That only Uses `lower-than`

Considering a function that receives three integer arguments, this function should return the highest value among them. Assertions can be used to enforce this condition, and an example code that tests this function can be seen below:

```Rust
fn main() {

    let a:usize = 42;
    let b:usize = -43;
    let c:usize = 0;

    let result = maximum(a, b, c);

    assert!(result >= a && result >= b && result >= c
        && (result == a || result == b || result == c ) );
}

fn maximum(a: usize, b: usize, c: usize) -> usize {
    // max(a, max(b, c))
    let max_ab = if a < b {b} else {a};
    if max_ab < c {c} else {max_ab}
}
```

Notice in this case that `a`, `b`, and `c` are concrete, fixed values. To turn the parameters of `maximum` into symbolic variables, we can obtain the representation of the function call to `maximum` executed using KMIR and then replace the concrete values of these variables with symbolic values. Furthermore, the assertion specified in the code can be manually translated as a requirement that should be met by the symbolic variables, meaning that any value that they can assume must respect the conditions contained in the specification. Following this approach, we can utilize KMIR to give us formal proof that, for any valid `isize` input, the maximum value among the three parameters will be returned.

Information on how the specification was created can be found in the longer [description of `maximum-proof`](https://github.com/runtimeverification/mir-semantics/tree/sample-challenge-11-proofs/rust-verification-proofs/maximum-proof).

To run this proof in your terminal from this folder, execute:

```Bash
cd maximum-proof
poetry -C ../../kmir/ run -- kmir prove run  $PWD/maximum-spec.k --proof-dir $PWD/proof
```

## Proof 2: Proving Unsafe Arithmetic Operations

The proofs in this section concern a section of the challenge of securing [Safety of Methods for Numeric Primitive Types](https://model-checking.github.io/verify-rust-std/challenges/0011-floats-ints.html#challenge-11-safety-of-methods-for-numeric-primitive-types) of the Verify Rust Standard Library Effort. Here, we implement proof of concepts of how KMIR can be used to prove the following unsafe methods according to their undefined behaviors: `unchecked_add`, `unchecked_sub`, `unchecked_mul`, `unchecked_shl`, `unchecked_shr`, and `unchecked_neg`.

For these functions, the proofs were carried out using variables of the `i16` integer type, and the criteria for triggering undefined behaviors for these methods were obtained in the [i16 type documentation page](https://doc.rust-lang.org/std/primitive.i16.html).

To obtain the specifications that prove the presence/absence of undefined behavior for these functions, analogous processes to the ones discussed in [Proof 1](#proof-1-proving-a-maximum-finding-function-that-only-uses-lower-than) were performed.

For an illustration of how we specify the requirements of the proof, which, in this case, are the assertions that would help us detect the presence/absence of undefined behavior in the unsafe methods, let's explore how we can prove safety conditions for the `unchecked_add` operation. Consider the following function:

https://github.com/runtimeverification/mir-semantics/blob/e2de329d009cde25f505819d7c8c9815571db9e7/rust-verification-proofs/unchecked_add/unchecked-add.rs#L11-L14

`unchecked_op` is a function that receives two `i16` arguments and executes an `unchecked_add` of the first parameter by the second, returning an `i16` value resulting from this operation. According to the [documentation of the unchecked_add function for the i16 primitive type](https://doc.rust-lang.org/std/primitive.i16.html#method.unchecked_add), considering the safety of this function "This results in undefined behavior when `self + rhs > i16::MAX or self + rhs < i16::MIN`, i.e. when `checked_add` would return `None`". By the process further disclosed in Proof 1, we can obtain a valid representation of a function call for `unchecked_op` and modify the variable values to be symbolic. The next step is to define the conditions these values should meet to verify safety conditions elaborated for `unchecked_add`. To this goal, see the following code snippet:

https://github.com/runtimeverification/mir-semantics/blob/e2de329d009cde25f505819d7c8c9815571db9e7/rust-verification-proofs/unchecked_add/unchecked-op-spec.k#L66-L73

The parameters for `unchecked_add` in this specification for KMIR are represented as A and B, which now are symbolic values. To specify the goal of our verification process, we implemented the above code snippet into the specification, which adds a requirement to the execution of our symbolic execution engine. In other words, our proof will only be successful if the specified requirements above are respected. 

In this `requires` clause, first, we use the semantics of K to specify A and B's boundaries, as `i16`s: `0 -Int (1 <<Int 15) <=Int A andBool A <Int (1 <<Int 15) andBool 0 -Int (1 <<Int 15) <=Int B andBool B <Int (1 <<Int 15)`. The next section of this `requires` clause specifies the safety conditions for the `unchecked_add` method: `andBool A +Int B <Int (1 <<Int 15) andBool 0 -Int (1 <<Int 15) <=Int A +Int B`.

To run the proofs for these functions, run the commands below, replacing `$METHOD_NAME` with the desired unsafe method name:

```Bash
cd $METHOD_NAME
poetry -C ../../kmir/ run -- kmir prove run  $PWD/unchecked-op-spec.k --proof-dir $PWD/proof 
```

The proof for `unchecked_add` is expected to work as described. Currently, we expect some of the other unsafe arithmetic proofs to manifest unpredicted behavior and end its execution prior to providing the proof's result. This behavior is due to an unfinished implementation of the operations under test and will be addressed in due course.
