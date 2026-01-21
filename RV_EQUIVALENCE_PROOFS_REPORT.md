# Solana SPL Token and P-Token Program Equivalence Proof

In this project, our goal is to demonstrate that the SPL Token and P-Token programs are _equivalent_.
More formally, we will verify that the P-Token program can _simulate_ the SPL-Token program, which, roughly speaking, states that for each SPL Token program state and instruction, there is an equivalent P-Token program state and instruction that does the exact same thing.

In the next section, we cover some technical preliminaries on the Solana blockchain itself and our proof methodology for the interested reader; everyone else should skip to the [Introduction section](#introduction).

## Technical Preliminaries

### Solana Programming Model

The Solana blockchain supports on-chain programmability via Solana _programs_, _accounts_, _messages_, and _instructions_.
Roughly speaking:

1.  A Solana _account_ is an addressable unit of mutable, on-chain data with the following fields:

    | Field Name | Description                                                    |
    | ---        | ---                                                            |
    | owner      | ID of program that owns this account                           |
    | lamports   | monetary balance of the account denominated in lamports        |
    | data       | bytes stored in account                                        |
    | executable | boolean flag that indicates whether this account is executable |
    | rent_epoch | the epoch when this account will next owe rent (deprecated)    |

    whose address is called its _key_.
    We also use the term _format_ when describing the particular data payloads that a program might store in one of its owned accounts.

2. A Solana _program_ is an account whose associated data is immutable and contains _executable code_[^program] and whose key is referred to as a _program ID_;
3. A Solana _message_ is a list of accounts (which are marked as either mutable, a signer, both, or neither) and a list of instructions;
4. A Solana _instruction_ is a program ID, a list of indices of message accounts, and an arbitrary, length-prefixed data payload that we refer to as the instruction's _format_.

Note that there are some special Solana programs called _native programs_ which have extra privileges above and beyond those of standard (non-native) programs; we will have more remarks to make about that later.

[^program]: Technically, in order to support upgradeability, the associated data of user-defined program accounts is actually just the address of some account that contains its executable data

The executable code of a Solana program must satisfy a few requirements:

1.  It must be encoded an [ELF](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) binary file that contains a Solana-specific variant of the [extended Berkeley Packet Filter (eBPF)](https://en.wikipedia.org/wiki/EBPF) virtual machine bytecode called _sBPF_ or sometimes just _SBF_.
2.  The ELF file must contain a function named `entrypoint`.
3.  The `entrypoint` function must have a single input argument which is a pointer to a byte array and return an unsigned 64-bit number as a status code (where 0 indicates success and any other number indicates failure).
3.  The input byte array must encode:

    1. the fields of all accounts passed to the program as well as their mutable/signer status and;
    2. the instruction format (i.e., an arbitrary length byte string);
    3. the ID of the program being invoked.

    using the encoding documented [here](https://github.com/solana-foundation/solana-com/blob/a8cee23bfc4d96326b8172a60539c8e7dea47ab3/content%2Fdocs%2Fen%2Fprograms%2Ffaq.mdx).

    Note that any passed in account may be modified by directly overwriting its serialized value in the input byte array; once execution completes, if the result was successful, the Solana validator runtime will commit the updated account state back to the account database.

Furthermore, the execution of each program instruction must satisfy a few invariants:

- the lamport balance of all accounts referenced in an instruction must be invariant
- changing the `owner` field of an account requires that the account's `data` is zeroed out
- accounts whose `executable` field is set to `true` cannot have their `data` or `owner` field mutated
- only the owner program of some account _A_ can:
  1. decrement _A_'s `lamports` field
  2. mutate any field of account _A_ that is not `lamports`
- only native programs can mutate an account's `executable` or `rent_epoch` fields

<!--
  -- * only built-in programs can change the `executable` or `rent_epoch` fields because:
  --   * the BPF interpreter deserialization logic does not commit updates to other fields
  --   * an `InvokeContext` handle is required to commit account info changes, but this context is not passed to user-defined programs
  -- * the runtime checks that account modifications performed by user-defined programs are permissible are performed once BPF interpreter execution completes; these checks are performed in two places:
  --   1. in `program_runtime::serialization::deserialize_parameters`, the `BorrowedInstructionAccount` setters `set_lamports`, `set_owner`, `set_data`
  --   2. in `svm::transaction_processor::TransactionBatchProcessor::execute_loaded_transaction`, the `transaction_accounts_lamports_sum` check
  -->

### Program Equivalence Primer

Abstractly, a program _P_ can be defined as by a set of _P-states_, an _initial P-state_, a set of operation/input labels $\Sigma$, and a set of _P-transitions_[^trans-system] where:

[^trans-system]: In general, a tuple containing a set of _states_, a set of _labels_, and a set of _labeled transitions_, is called a _labeled transition system_ in the computer science literature.

1.  An individual _P-state_ is a snapshot of the program's world in a particular moment in time; it fully describes what the program is currently doing as well as what it will do next;
2.  The _initial P-state_, denoted $initial(P)$, is the designated state from which program execution begins;
3.  Given two P-states _a_ and _b_ and a label $\sigma$, we define a _P-transition_ (denoted $a \overset{\sigma}{\rightarrow} b$) as a rule which permits program _P_, upon receiving an input or performing an operation $\sigma\in\Sigma$, to transition from _P_-state _a_ to _b_. In case such a transition exists, we say that _a_ is a predecessor of _b_ or _b_ is a successor of _a_.

It is sometimes useful to talk about properties that describe a particular set of _P_-states; formally, we call such a property a _predicate_.
Graphically, we denote membership of a state _a_ in a predicate $\Phi$ by writing $a\in\Phi$.
Given two predicates $\Phi$ and $\Psi$, we write $\Phi \subseteq \Psi$ to mean every state in $\Phi$ is also contained in $\Psi$.

One important predicate is $reach(P)$, the set of _reachable_ _P_-states, defined as the smallest set of _P_-states that:

   1. contains P's initial state and;
   2. contains all successor P-states of any reachable P-state.

Given some predicate $\Iota$, whenever $reach(P) \subseteq \Iota$, we say that $\Iota$ is an _invariant_.
Furthermore, if we have a predicate $\Iota$ that:

1. holds for the initial P-state;
2. for each pair of reachable P-states _a_ and _b_ and transition $a \overset{\sigma}{\rightarrow} b$, assuming $a\in\Iota$, we can prove that $b\in\Iota$;

then we say that $\Iota$ is an _inductive invariant_.

With this framework, we can now discuss what we mean when we say that some program _P_ _simulates_ another program _Q_.
To begin, since programs _P_ and _Q_ are different, they will have different kinds of states[^programlabels].
So we need a notion of _state equivalence_, or a way to associate _P_-states to _Q_-states that mean the same thing.
Graphically, we denote equivalences with a triple-bar symbol $(\equiv)$.
We can now present our key definition:

A program _P_ _simulates_ a program _Q_ if and only if,

1. $initial(P) \equiv initial(Q)$
2. for each pair of states $a,a'\in reach(Q)$ and _Q_-transition $a\overset{\sigma}{\rightarrow} a'$, there exists _P_-states _b_ and _b'_ such that:
   - $a \equiv b$
   - $a' \equiv b'$
   - $b\overset{\sigma}{\rightarrow} b'$ is a valid _P_-transition

[^programlabels]: Of course, programs _P_ and _Q_ will also have different kinds of operations, but since we assume that _P_ is designed as a re-implementation of _Q_, we require that if _Q_ has some operation _op_, then _P_ also has operation _op_ (though _P_ may have unique operations not contained in _Q_).

Sometimes, we may not want to consider the entire set of possible operations/inputs for a program $P$, but only a subset of them.
Given a program _P_ with operations/inputs $\Sigma$, define the _restriction_ of _P_ to $\Sigma_0\subseteq \Sigma$ (denoted $P|_{\Sigma_0}$) as a program with the same states and initial state as $P$, the set of operations/inputs $\Sigma_0$, where $P|_{\Sigma_0}$ contains the $P$-transition $a\overset{\sigma}{\rightarrow}b$ whenever $\sigma\in\Sigma_0$.

### Formal Verification Methodology

To verify that the P-Token program simulates the SPL Token program, we follow a particular formal verification methodology which breaks down the equivalence into a few parts.
We survey our overall methodology in Figure 1 below:

```
┏━━━━━━━━━━━━━━━━━━━━━┓               ┏━━━━━━━━━━━━━━━━━━━━━┓
┃ SPL Token Rust Code ┃               ┃  P-Token Rust Code  ┃
┗━━━━━━━━━━━━━━━━━━━━━┛               ┗━━━━━━━━━━━━━━━━━━━━━┛     Rust-to-K-MIR Compilation
-----------🡻-------------------------------------🡻---------------------------------------
┏━━━━━━━━━━━━━━━━━━━━━┓               ┏━━━━━━━━━━━━━━━━━━━━━┓
┃ SPL Token MIR Code  ┃               ┃   P-Token MIR Code  ┃       MIR Program Interpreter
┗━━━━━━━━━━━━━━━━━━━━━┛               ┗━━━━━━━━━━━━━━━━━━━━━┛    Generation via K Framework
-----------🡻-------------------------------------🡻---------------------------------------
┏━━━━━━━━━━━━━━━━━━━━━━┓              ┏━━━━━━━━━━━━━━━━━━━━━┓
┃  SPL Token Concrete  ┃              ┃  P-Token Concrete   ┃            State Abstraction/
┃    MIR Semantics     ┃              ┃    MIR Semantics    ┃               Reachable State 
┗━━━━━━━━━━━━━━━━━━━━━━┛              ┗━━━━━━━━━━━━━━━━━━━━━┛            Over-Approximation 
-----------🡻-------------------------------------🡻---------------------------------------
┏━━━━━━━━━━━━━━━━━━━━━━┓              ┏━━━━━━━━━━━━━━━━━━━━━┓
┃  SPL Token Symbolic  ┃              ┃  P-Token Symbolic   ┃   
┃    MIR Semantics     ┃              ┃    MIR Semantics    ┃  Instruction Variant Specific         
┗━━━━━━━━━━━━━━━━━━━━━━┛              ┗━━━━━━━━━━━━━━━━━━━━━┛            Input Partitioning
-----------🡻-------------------------------------🡻---------------------------------------
┏━━━━━━━━━━━━━━━━━━━━━━┓              ┏━━━━━━━━━━━━━━━━━━━━━┓
┃      SPL Token       ┃              ┃      P-Token        ┃
|  Instruction Variant ┃              ┃ Instruction Variant ┃
┃  Symb. MIR Semantics ┃              ┃ Symb. MIR Semantics ┃          
┗━━━━━━━━━━━━━━━━━━━━━━┛              ┗━━━━━━━━━━━━━━━━━━━━━┛          Big-Step Abstraction
-----------🡻-------------------------------------🡻---------------------------------------
┏━━━━━━━━━━━━━━━━━━━━━━┓              ┏━━━━━━━━━━━━━━━━━━━━━┓
┃      SPL Token       ┃              ┃      P-Token        ┃
┃       Labeled        ┃  =========>  ┃      Labeled        ┃
|  Transition System   ┃              ┃  Transition System  ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛              ┗━━━━━━━━━━━━━━━━━━━━━┛              Check Simulation
-------------------------------------------------------------------------------------------

                           Figure 1.
                 Formal Verification Methodology
```

There are many details to discuss, but, to summarize the entire process in a single sentence:

We perform a multi-phase abstraction of the SPL Token and P-Token programs that converts their Rust source into labeled transitions systems with identical states and identical labels where we can apply standard program simulation checks using standard equality as our state equivalence relation.

Let us now break down the formal equivalence check methodology step-by-step:

1. Compile Rust to MIR via KMIR Rust Compiler

   We use a modified version of the Rust compiler that emits a simplified version of Rust code referred to as the Rust compiler's Mid-level Intermediate Representation (MIR) for use with the K symbolic proof engine; compared to standard Rust code, in MIR code:

   - all references to module items are fully qualified;
   - all generic items are fully [monomorphized](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html);
   - static and constant module items are assigned to literal byte strings;
   - all variable `drop`s at end-of-scope are made explicit;
   - all local variable names are replaced with numeric identifiers;
   - implicit borrows are inserted;
   - implicit closure structures are generated
   - etc...

   The reason why we use MIR [^mir] instead of Rust source code is its _simplicity_ mentioned above;
   using MIR lets us fully capture the behavior of Rust programs without worrying about complexities like:

   - trait instance validation
   - borrow checking
   - type layout and alignment

[^mir]: In particular we extract Stable / Public MIR, which is a version of MIR intended for analysis tools to access

2. Generate Program-Specific Concrete Semantics via $\mathbb{K}$ Formal Verification Framework + MIR Semantics

   The $\mathbb{K}$ framework is a toolkit for designing and modeling any programming language (PL) and also for formally reasoning about programs in a particular language.
   The $\mathbb{K}$ framework takes a formal PL semantics and generates a suite of correct-by-construction tools for that specific PL including:

   - a parser and unparser
   - a concrete interpreter
   - a symbolic execution engine and theorem prover

   In this step, we use our MIR semantics as an input to the $\mathbb{K}$ framework in order to create a MIR interpreter.
   For those unfamiliar with the idea, a program language semantics is a complete set of rules that defines precisely how well-formed MIR programs behave.
   We then pass our MIR source programs as an input to the MIR interpreter and obtain a semantics for SPL Token and P-Token programs, i.e., program-specific interpreters which consume SPL Token/P-Token formatted byte strings as inputs and return a status code as an output.

   The goal of this step is to precisely capture of the SPL Token and P-Token programs so that we can analyze them.
   The correct-by-construction nature of these generated tools ensures _soundness_, i.e., if our semantics witness a particular state, then that state is reachable when we execute the actual program.

   Note that, in order conservatively over-approximate real implementations, a semantics will get stuck on undefined behaviors (while in practice, the Rust compiler will choose some arbitrary behavior).

3. Generate Program-Specific Symbolic Semantics via State Abstraction/Reachable State Over-approximation

   While examining the behavior of the program-specific formal semantics from step (2) might seem sufficient, we cannot be certain, when we execute them, that we will cover _all_ possible program states.
   So in this step, we over-approximate the entire set of reachable program states using a constrained term and update our semantics to now perform execution symbolically beginning from this abstract state.
   The goal of making this move is to ensure _completeness_, i.e., if the source programs can perform some behavior, than when we execute our symbolic semantics, we will be able to reproduce.
   Note that, as part of this shift, we also rely on $\mathbb{K}$'s built-in theorem proving capabilities that let us use matching logic, co-induction, and SMT solvers to reason about (a potentially infinite number of) program states and transitions in a finite amount of time[^limitations].

4. Generate Program+Instruction-Variant-Specific Symbolic Semantics via Input Partitioning

   While state abstraction alone ensures completeness of reasoning, it makes for very large and complex proofs.
   To counteract this tendency, we perform a per-instruction-variant partitioning of the abstract input space.
   In essence, after performing this partitioning, we obtain a per-instruction-variant-specific symbolic semantics for the SPL Token and P-Token programs that can only accept a particular instruction variant (e.g., one variant only accepts `Transfer`s, one variant only accepts `InitializeAccount`, etc...).
   As mentioned above, we don't gain any additional reasoning capabilities by making this move; this is purely _proof engineering_.
   In essence, this is a form of _modularization_, and the payoffs exactly mirror those that we experience in broader software development world.

5. Perform a Big-Step Semantics Style Abstraction

   In this step, we apply a big-step semantics style abstraction to our semantics.
   For those familiar with big-step style semantics, they evaluate a program, from its initial state to its final state, in one-shot.
   By that we mean, the notion of intermediate states is entirely dropped.
   Here, we view each execution of the SPL Token or P-Token program as just a quadruple that contains:

   1. an input state (a set of program-owned accounts with certain keys, lamport balances, and data payloads)
   2. a string of input instruction bytes
   3. an unsigned 64-bit output status code
   4. an output state (also a set of program-owned accounts with certain keys, lamport balances, and data payloads)

   By concatenating items (2)-(3) together into a single item, we now have just what we need to construct a labelled transition system where:

   - states are partial functions from account keys to pairs of lamport balances and data payloads;
   - transitions are triples containing an input state, a label (which is a pair of an instruction format plus the return code obtained from executing that instruction format), and an output state.

6. Check Simulation; Show When Provided Identical Pre-states/Inputs, Identical Post-States Reached
   
   Finally, to check that the P-Token program actually simulates the SPL Token program, we execute each instruction-specific semantics for SPL Token and P-Token from the same starting symbolic state with the same symbolic input.
   We then verify that each execution reaches an identical set of symbolic output states.
   This is equivalent to _batching_ the required P-Token-can-copy-SPL-Token-moves checks instead of checking that for each individual SPL-Token transition, we can find a corresponding individual P-Token transition.
   In fact, without this batching, performing an exhaustive simulation check would be extremely difficult (if not impossible) on modern hardware.

[^limitations]: Note that there is no free lunch and symbolic execution is not a panacea that can be trivially used to solve all verification problems. In certain cases, we must provide the execution engine
with lemmas (in other words, hints) that help the execution engine make progress when it gets stuck.

Now that we have surveyed the entire equivalence check process, there are a few details that we need to fill in.
We needed to prove the following lemmas by hand in order for the verification to work:

1. We manually prove that any valid SPL Token instruction format is also valid for P-Token.
   This means that any P-Token instruction format is byte-for-byte compatible with SPL Token.

2. We manually derive and prove an inductive invariant $\Iota$ for _both_ SPL Token and P-Token and use this as our reachable state over-approximation.
   This invariant is the union of the following properties:

   1. The account formats for all SPL Token (resp. P-Token) owned accounts are either:

      - fully zeroed out (when the account is uninitialized) or;
      - correspond to an encoded and properly initialized Mint, Token Account, or Multisig.

      An easy corollary of (1) is that the total set of states (ignoring reachability) that the SPL Token or P-Token program can take on are identical.

   2. The `lamports` field for all SPL Token (resp. P-Token) owned accounts is sufficient for rent exemption

   3. For a given Mint, the sum of all Token Account balances for that Mint equals the Mint's supply

   4. The `lamports` field for a native Token Account is greater than or equal to the Token Account's balance plus its rent exemption price.

## Introduction

The Solana Programming Library (SPL) is a set of Solana-specific programs and libraries, written in the Rust programming language, that can be used to create custom dApps for Solana. An important component of the SPL toolkit is the SPL Token Program, a program that enables the creation and usage of custom fungible and non-fungible tokens on the Solana blockchain. 

As the name indicates, the SPL Token Program contains the source code for a deployable program on Solana.
Like other kinds of Solana programs, the SPL Token program has:

1. a handful of data format variant that can be stored in any account owned by the Token program;
2. a handful of instruction format variants that instruct the program to perform various operations.

We will describe these formats more fully below.

As usage of the SPL Token Program increased, eventually, a compute-optimized version of the SPL Token Program was proposed in Solana Improvement Document (SIMD-0266) by febo and Jon Cinque.
The idea: a program with byte-for-byte equivalent account and instruction formats that operates more efficiently, using less validator time, and thus permitting more instructions to be validated in a single Solana slot.

### SPL Token Account Format Variants

As discussed in the [Solana Programming Model](#solana-programming-model) section, the accounts that are owned by a particular program are used to store that program's state.
However, recall that Solana does not have runtime-enforced type checking of values stored in an account's `data` field.
Thus, determining what kinds of values a program permits saving as its owned account's `data` requires a careful reading of the program source code.
To aid with this task, the SPL provides a few packages to aid in account manipulation:

- solana-account-info - a data structure `AccountInfo` that represents the Solana account structure
- solana-program-entrypoint - an entrypoint wrapper macro that parses all encoded Solana accounts and deserializes them into a slice of `AccountInfo`s and also extracts the instruction format
- solana-program-pack - provides a `Pack` helper trait that can be used to de/serialize encoded values in the `data` field of `AccountInfo` that always checks length of the slice used as the de/serialization source/target.

By a quick scan of the source code, we see that:

- a slice containing all `AccountInfo`s passed to the entrypoint are created by the solana-program-entrypoint package;
- all `AccountInfo`s are accessed via the `next_account_info` iterator helper function;
- all writes to `AccountInfo.data` occurs via a call to the `Pack` trait's `pack` function.

Essentially, this means that, assuming that the solana-program-entrypoint package correctly initializes `AccountInfo` and the called `pack` implementations are consistent, then we know that only `pack`able data will be stored in accounts owned by the SPL Token program.

From the above argumentation, we can determine that the account data format has the following variants (note that the data is densely packed, i.e., stored without any padding):

1. Account (165 bytes)
   - key of mint account (32 bytes)
   - key of owner account (32 bytes)
   - `u64` account balance (8 bytes) 
   - optional key of delegate account (36 bytes - 4 bytes for option tag + 32 bytes for key)
   - fieldless account state enumeration (1 byte)
   - optional native rent exempt reserve amount (12 bytes - 4 bytes for option tag + 8 bytes for `u64` amount)
   - `u64` amount authorized for delegate to spend (8 bytes)

2. Mint (82 bytes)
   - optional key of mint authority (36 bytes - 4 bytes for option tag + 32 bytes for key)
   - `u64` total supply of all non-native minted tokens - (8 bytes)
   - `u8` number of decimals for minted token units - (1 byte)
   - `bool` initialized indicator - (1 byte)
   - optional key for freeze authority (36 bytes - 4 bytes for option tag + 32 bytes for key)

3. Multisig (355 bytes)
   - `u8` number of signers required - (1 byte)
   - `u8` number of valid signers - (1 byte)
   - `bool` initialized indicator - (1 byte)
   - `[Pubkey; 11]` fixed size valid signers array - (11 * 32 = 352 bytes)

### SPL Token Instruction Formats

We analyze the byte layout of instruction format variants.
To do this, we examine the SPL Token program entrypoint and check how the instruction format is parsed.
There is a single parser function that is called `TokenInstruction::unpack`.
This parser function determines that the various instruction format variants have the following layouts:

| Enum Tag | Enum Variant             | Associated Data                                           | Comment                                                   |
| ---      | ---                      | ---                                                       | ---                                                       |
|   0      | InitializeMint           | u8, Pubkey:MintAuthority, COption<Pubkey>:FreezeAuthority |                                                           |
|   1      | InitializeAccount        |                                                           |                                                           |
|   2      | InitializeMultisig       | u8                                                        |                                                           |
|   3      | Transfer                 | u64                                                       |                                                           |
|   4      | Approve                  | u64                                                       |                                                           |
|   5      | Revoke                   |                                                           |                                                           |
|   6      | SetAuthority             | AuthorityType, COption<Pubkey>:NewAuthority               | AuthorityType == AccountOwner => is_defined(NewAuthority) |
|   7      | MintTo                   | u64                                                       |                                                           |
|   8      | Burn                     | u64                                                       |                                                           |
|   9      | CloseAccount             |                                                           |                                                           |
|  10      | FreezeAccount            |                                                           |                                                           |
|  11      | ThawAccount              |                                                           |                                                           |
|  12      | TransferChecked          | u64, u8                                                   |                                                           |
|  13      | ApproveChecked           | u64, u8                                                   |                                                           |
|  14      | MintToChecked            | u64, u8                                                   |                                                           |
|  15      | BurnChecked              | u64, u8                                                   |                                                           |
|  16      | InitializeAccount2       | Pubkey:Owner                                              |                                                           |
|  17      | SyncNative               |                                                           |                                                           |
|  18      | InitializeAccount3       | Pubkey:Owner                                              |                                                           |
|  19      | InitializeMultisig2      | u8                                                        |                                                           |
|  20      | InitializeMint2          | u8, Pubkey:MintAuthority, COption<Pubkey>:FreezeAuthority |                                                           |
|  21      | GetAccountDataSize       |                                                           |                                                           |
|  22      | InitializeImmutableOwner |                                                           |                                                           |
|  23      | AmountToUiAmount         | u64                                                       |                                                           |
|  24      | UiAmountToAmount         | &str                                                      |                                                           |

Note that the P-Token program has two additional instruction format variants that SPL Token does not have.
However, we will not examine these further since they are not relevant for the equivalence proof.

| Enum Tag | Enum Variant             | Associated Data                                           | Comment                                                   |
| ---      | ---                      | ---                                                       | ---                                                       |
|  38      | WithdrawExcessLamports   |                                                           |                                                           |
| 255      | Batch                    | (accts:u8,len:u8,len)*                                    |                                                           |

| Enum Tag | AuthorityType Variant |
| ---      | ---                   |
| 0        | MintTokens            |
| 1        | FreezeAccount         |
| 2        | AccountOwner          |
| 3        | CloseAccount          |

| Universal Failure Cases |
| ---                     |
| Input Too Short         |
| Not Enough Accounts     |

## Proof Body Overview

Here, we provide an overview of the proof process in plain English; the actual automated proofs are contained in our proof script files which are located in our [solana-token repository fork](https://github.com/runtimeverification/solana-token) at the following paths:

- p-token/src/entrypoint-runtime-verification.rs
- program/src/entrypoint-runtime-verification.rs

Instead, in this section, for each instruction format variant, for both the SPL Token and P-Token programs, we list:

1. the handler function for that instruction format variant;
2. the various checks and effects performed by that instruction variant handler function for both the SPL Token and P-Token programs.

We can then compare the executed checks and effects at a high level and show that they agree by:

1. showing that each check and effect is performed by each in the same order or;
2. if any check/effect is added/removed/swapped, showing that the addition/removal/swap cannot cause the programs' outcomes to diverge.

First, let's review the handler functions for each variant.
In both the SPL Token and P-Token programs, these handler functions have a similar structure.
They assume that the `AccountInfo` structs and instruction format variant have already been parsed from the `entrypoint()` `input` string.
Then these handlers receive as input the entire slice of accounts parsed by the `entrypoint` function as well as any instruction format embedded data.
This means, before one of these handlers is called, assuming the Solana runtime properly invokes the program entrypoint, then the only way that execution can fail is if an invalid instruction format variant is passed as input to the `entrypoint` function.

| Instruction Variant      | SPL Token Handler                                             | P-Token Handler                                                                          |
| ---                      | ---                                                           | ---                                                                                      |
| InitializeMint           | program/src/processor.rs / process_initialize_mint            | program/src/processor/initialize_mint.rs / process_initialize_mint                       |
| InitializeAccount        | program/src/processor.rs / process_initialize_account         | program/src/processor/initialize_account.rs / process_initialize_account                 |
| InitializeMultisig       | program/src/processor.rs / process_initialize_multisig        | program/src/processor/initialize_multisig.rs / process_initialize_multisig               |
| Transfer                 | program/src/processor.rs / process_transfer                   | program/src/processor/transfer.rs / process_transfer                                     |
| Approve                  | program/src/processor.rs / process_approve                    | program/src/processor/approve.rs / process_approve                                       |
| Revoke                   | program/src/processor.rs / process_revoke                     | program/src/processor/revoke.rs / process_revoke                                         |
| SetAuthority             | program/src/processor.rs / process_set_authority              | program/src/processor/set_authority.rs / process_set_authority                           |
| MintTo                   | program/src/processor.rs / process_mint_to                    | program/src/processor/mint_to.rs / process_mint_to                                       |
| Burn                     | program/src/processor.rs / process_burn                       | program/src/processor/burn.rs / process_burn                                             |
| CloseAccount             | program/src/processor.rs / process_close_account              | program/src/processor/close_account.rs / process_close_account                           |
| FreezeAccount            | program/src/processor.rs / process_toggle_freeze_account      | program/src/processor/freeze_account.rs / process_toggle_freeze_account                  |
| ThawAccount              | program/src/processor.rs / process_toggle_freeze_account      | program/src/processor/thaw_account.rs / process_toggle_freeze_account                    |
| TransferChecked          | program/src/processor.rs / process_transfer                   | program/src/processor/transfer_checked.rs / process_transfer_checked                     |
| ApproveChecked           | program/src/processor.rs / process_approve                    | program/src/processor/approve_checked.rs / process_approve_checked                       |
| MintToChecked            | program/src/processor.rs / process_mint_to                    | program/src/processor/mint_to_checked.rs / process_mint_to_checked                       |
| BurnChecked              | program/src/processor.rs / process_burn                       | program/src/processor/burn_checked.rs / process_burn_checked                             |
| InitializeAccount2       | program/src/processor.rs / process_initialize_account2        | program/src/processor/initalize_account2.rs / process_initialize_account2                |
| SyncNative               | program/src/processor.rs / process_sync_native                | program/src/processor/sync_native.rs / process_sync_native                               |
| InitializeAccount3       | program/src/processor.rs / process_initialize_account3        | program/src/processor/initialize_account3.rs / process_initialize_account3               |
| InitializeMultisig2      | program/src/processor.rs / process_initialize_multisig2       | program/src/processor/initialize_multisig2.rs / process_initialize_multisig2             |
| InitializeMint2          | program/src/processor.rs / process_initialize_mint2           | program/src/processor/initialize_mint2.rs / process_initialize_mint2                     |
| GetAccountDataSize       | program/src/processor.rs / process_get_account_data_size      | program/src/processor/get_account_data_size.rs / process_get_account_data_size           |
| InitializeImmutableOwner | program/src/processor.rs / process_initialize_immutable_owner | program/src/processor/initialize_immutable_owner.rs / process_initialize_immutable_owner |
| AmountToUiAmount         | program/src/processor.rs / process_amount_to_ui_amount        | program/src/processor/amount_to_ui_amount.rs / process_amount_to_ui_amount               |
| UiAmountToAmount         | program/src/processor.rs / process_ui_amount_to_amount        | program/src/processor/ui_amount_to_amount.rs / process_ui_amount_to_amount               |

For each of these variants above, we list, in plain English, the checks and effects performed by each handler (labeled by `C` and `E` respectively).
If, for both SPL Token and P-Token, the checks and effects are identical and performed in an identical manner, we will only list them once.
Otherwise, if there are any differences in the checks and effects that are performed or in how they are performed, we will make note of those discrepancies.
Additionally, for certain related instruction variants, we may list them together if they share an implementation.

| Instruction Variant      | Check/Effect                                                                                                                                      | Comment                                    |
| ---                      | ---                                                                                                                                               | ---                                        |
| InitializeMint           | C: ACCOUNT ARITY >= 2                                                                                                                             |                                            |
|                          | E: LOAD RENT-EXEMPTION LAMPORTS FROM ACCOUNT AT INDEX 1                                                                                           |                                            |
|                          | C: ACCOUNT AT INDEX 0 (MINT ACCOUNT) IS UNINITIALIZED MINT ACCOUNT                                                                                |                                            |
|                          | C: MINT ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                         |                                            |
|                          | E: WRITE MINT DATA TO MINT ACCOUNT                                                                                                                | P-ONLY: Writes are implicit                |
| InitializeMint2          | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | E: COMPUTE RENT-EXEMPTION LAMPORTS FROM RENT SYSCALL                                                                                              |                                            |
|                          | C: ACCOUNT AT INDEX 0 (MINT ACCOUNT) IS UNINITIALIZED MINT ACCOUNT                                                                                |                                            |
|                          | C: MINT ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                         |                                            |
|                          | E: WRITE MINT DATA TO MINT ACCOUNT                                                                                                                | P-ONLY: Writes are implicit                |
| InitializeAccount        | C: ACCOUNT ARITY >= 4                                                                                                                             |                                            |
|                          | E: LOAD RENT-EXEMPTION LAMPORTS FROM ACCOUNT AT INDEX 3                                                                                           |                                            |
|                          | C: ACCOUNT AT INDEX 0 (TARGET ACCOUNT) IS UNINITIALIZED TOKEN ACCOUNT                                                                             |                                            |
|                          | C: TARGET ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                       |                                            |
|                          | C: ACCOUNT AT INDEX 1 (MINT ACCOUNT) IS OWNED BY PROGRAM (IF MINT ACCOUNT IS NON-NATIVE)                                                          |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT (IF MINT ACCOUNT IS NON-NATIVE )                                                                              |                                            |
|                          | E: COMPUTE TARGET ACCOUNT BALANCE                                                                                                                 |                                            |
|                          | E: WRITE ACCOUNT DATA WITH OWNER SET TO KEY OF ACCOUNT AT INDEX 2                                                                                 | P-ONLY: Writes are implicit                |
| InitializeAccount2       | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | E: LOAD RENT-EXEMPTION LAMPORTS FROM ACCOUNT AT INDEX 2                                                                                           |                                            |
|                          | C: ACCOUNT AT INDEX 0 (TARGET ACCOUNT) IS UNINITIALIZED TOKEN ACCOUNT                                                                             |                                            |
|                          | C: TARGET ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                       |                                            |
|                          | C: ACCOUNT AT INDEX 1 (MINT ACCOUNT) IS OWNED BY PROGRAM (IF MINT ACCOUNT IS NON-NATIVE)                                                          |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT (IF MINT ACCOUNT IS NON-NATIVE )                                                                              |                                            |
|                          | E: COMPUTE TARGET ACCOUNT BALANCE                                                                                                                 |                                            |
|                          | E: WRITE ACCOUNT DATA WITH OWNER SET TO OWNER KEY PARAMETER                                                                                       | P-ONLY: Writes are implicit                |
| InitializeAccount3       | C: ACCOUNT ARITY >= 2                                                                                                                             |                                            |
|                          | E: COMPUTE RENT-EXEMPTION LAMPORTS FROM RENT SYSCALL                                                                                              |                                            |
|                          | C: ACCOUNT AT INDEX 0 (TARGET ACCOUNT) IS UNINITIALIZED TOKEN ACCOUNT                                                                             |                                            |
|                          | C: TARGET ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                       |                                            |
|                          | C: ACCOUNT AT INDEX 1 (MINT ACCOUNT) IS OWNED BY PROGRAM (IF MINT ACCOUNT IS NON-NATIVE)                                                          |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT (IF MINT ACCOUNT IS NON-NATIVE )                                                                              |                                            |
|                          | E: COMPUTE TARGET ACCOUNT BALANCE                                                                                                                 |                                            |
|                          | E: WRITE ACCOUNT DATA WITH OWNER SET TO OWNER KEY PARAMETER                                                                                       | P-ONLY: Writes are implicit                |
| InitializeMultisig       | C: ACCOUNT ARITY >= 2                                                                                                                             |                                            |
|                          | C: LOAD RENT-EXEMPTION LAMPORTS FROM ACCOUNT AT INDEX 1                                                                                           |                                            |
|                          | C: ACCOUNT AT INDEX 0 (MULTISIG ACCOUNT) IS UNINITIALIZED MULTISIG                                                                                |                                            |
|                          | C: MULTISIG ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                     |                                            |
|                          | C: ACCOUNT ARITY - 2 IS A VALID MULTISIG SIGNER ARITY                                                                                             |                                            |
|                          | C: REQUIRED SIGNATURES PARAMETER IS A VALID MULTISIG SIGNER ARITY                                                                                 |                                            |
|                          | E: WRITE MULTISIG ACCOUNT DATA                                                                                                                    | P-ONLY: Writes are implicit                |
| InitializeMultisig2      | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | C: COMPUTE RENT-EXEMPTION LAMPORTS FROM RENT SYSCALL                                                                                              |                                            |
|                          | C: ACCOUNT AT INDEX 0 (MULTISIG ACCOUNT) IS UNINITIALIZED MULTISIG                                                                                |                                            |
|                          | C: MULTISIG ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                     |                                            |
|                          | C: ACCOUNT ARITY - 1 IS A VALID MULTISIG SIGNER ARITY                                                                                             |                                            |
|                          | C: REQUIRED SIGNATURES PARAMETER IS A VALID MULTISIG SIGNER ARITY                                                                                 |                                            |
|                          | E: WRITE MULTISIG ACCOUNT DATA                                                                                                                    | P-ONLY: Writes are implicit                |
| InitializeImmutableOwner | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (TARGET ACCOUNT) IS UNINITIALIZED TOKEN ACCOUNT                                                                             |                                            |
| CloseAccount             | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) AND ACCOUNT AT INDEX 1 (DESTINATION ACCOUNT) ARE DISTINCT                                                  |                                            |
|                          | C: SOURCE ACCOUNT IS WELL-FORMED TOKEN ACCOUNT                                                                                                    |                                            |
|                          | C: SOURCE ACCOUNT IS NATIVE OR AMOUNT IS ZERO                                                                                                     |                                            |
|                          | C: SOURCE ACCOUNT CLOSE AUTHORITY OR OWNER IS A SIGNER ACCOUNT AT INDEX 2 (IF SOURCE ACCOUNT NOT OWNED BY SYSTEM/INCINERATOR PROGRAM)             |                                            |
|                          | C: DESTINATION IS INCINERATOR (IF SOURCE ACCOUNT IS OWNED BY SYSTEM/INCINERATOR PROGRAM)                                                          |                                            |
|                          | E: TRANSFER ALL LAMPORTS FROM SOURCE TO DESTINATION                                                                                               |                                            |
|                          | E: ZERO OUT SOURCE ACCOUNT DATA                                                                                                                   |                                            |
| Approve                  | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: SOURCE ACCOUNT OWNER IS A SIGNER ACCOUNT AT INDEX 2                                                                                            |                                            |
|                          | E: ON SOURCE ACCOUNT, SET DELEGATE TO KEY OF ACCOUNT AT INDEX 1 AND DELEGATED AMOUNT                                                              |                                            |
| ApproveChecked           | C: ACCOUNT ARITY >= 4                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: SOURCE ACCOUNT MINT KEY MATCHES KEY OF ACCOUNT AT INDEX 1 (MINT ACCOUNT)                                                                       |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT                                                                                                               |                                            |
|                          | C: EXPECTED DECIMALS PARAMETER MATCHES MINT ACCOUNT EXPECTED DECIMALS                                                                             |                                            |
|                          | C: SOURCE ACCOUNT OWNER IS A SIGNER ACCOUNT AT INDEX 3                                                                                            |                                            |
|                          | E: ON SOURCE ACCOUNT, SET DELEGATE TO KEY OF ACCOUNT AT INDEX 2 AND DELEGATED AMOUNT                                                              |                                            |
| Revoke                   | C: ACCOUNT ARITY >= 2                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: SOURCE ACCOUNT OWNER IS A SIGNER ACCOUNT AT INDEX 1                                                                                            |                                            |
|                          | E: ON SOURCE ACCOUNT, CLEAR DELEGATE KEY AND DELEGATED AMOUNT                                                                                     |                                            |
| Burn                     | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: ACCOUNT AT INDEX 1 (MINT ACCOUNT) IS WELL-FORMED MINT                                                                                          |                                            |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: MINT IS NOT NATIVE                                                                                                                             |                                            |
|                          | C: SOURCE TOKEN AMOUNT >= BURN AMOUNT                                                                                                             |                                            |
|                          | C: SOURCE ACCOUNT MINT KEY MATCHES KEY OF MINT ACCOUNT                                                                                            |                                            |
|                          | C: SOURCE ACCOUNT OWNER OR DELEGATE IS A SIGNER ACCOUNT AT INDEX 2 (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR)                                |                                            |
|                          | C: DELEGATED AMOUNT >= BURN AMOUNT (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR AND DELEGATE IS SIGNER)                                         |                                            |
|                          | E: DELEGATED AMOUNT IS DECREMENTED (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR AND DELEGATE IS SIGNER)                                         |                                            |
|                          | E: DELEGATE ADDRESS IS CLEARED (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR AND DELEGATE IS SIGNER AND DELEGATED AMOUNT == TRANSFER AMOUNT)     |                                            |
|                          | C: SOURCE ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                                    |                                            |
|                          | C: MINT ACCOUNT OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                                         |                                            |
|                          | E: EARLY TERMINATE (IF ZERO TRANSFER)                                                                                                             | P-ONLY                                     |
|                          | E: UPDATE SOURCE ACCOUNT TOKEN AMOUNT                                                                                                             |                                            |
|                          | E: UPDATE MINT TOTAL SUPPLY                                                                                                                       |                                            |
| BurnChecked              | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: ACCOUNT AT INDEX 1 (MINT ACCOUNT) IS WELL-FORMED MINT                                                                                          |                                            |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: MINT IS NOT NATIVE                                                                                                                             |                                            |
|                          | C: SOURCE TOKEN AMOUNT >= BURN AMOUNT                                                                                                             |                                            |
|                          | C: SOURCE ACCOUNT MINT KEY MATCHES KEY OF MINT ACCOUNT                                                                                            |                                            |
|                          | C: EXPECTED DECIMALS PARAMETER MATCHES MINT ACCOUNT EXPECTED DECIMALS                                                                             |                                            |
|                          | C: SOURCE ACCOUNT OWNER OR DELEGATE IS A SIGNER ACCOUNT AT INDEX 2 (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR)                                |                                            |
|                          | C: DELEGATED AMOUNT >= BURN AMOUNT (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR AND DELEGATE IS SIGNER)                                         |                                            |
|                          | E: DELEGATED AMOUNT IS DECREMENTED (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR AND DELEGATE IS SIGNER)                                         |                                            |
|                          | E: DELEGATE ADDRESS IS CLEARED (IF NOT OWNED BY SYSTEM PROGRAM OR INCINERATOR AND DELEGATE IS SIGNER AND DELEGATED AMOUNT == TRANSFER AMOUNT)     |                                            |
|                          | C: SOURCE ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                                    |                                            |
|                          | C: MINT ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                                      |                                            |
|                          | E: EARLY TERMINATE (IF ZERO TRANSFER)                                                                                                             | P-ONLY                                     |
|                          | E: UPDATE SOURCE ACCOUNT TOKEN AMOUNT                                                                                                             |                                            |
|                          | E: UPDATE MINT TOTAL SUPPLY                                                                                                                       |                                            |
| MintTo                   | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 1 (DESTINATION ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                          |                                            |
|                          | C: DESTINATION ACCOUNT IS NOT FROZEN                                                                                                              |                                            |
|                          | C: DESTINATION ACCOUNT IS NOT NATIVE                                                                                                              |                                            |
|                          | C: DESTINATION ACCOUNT MINT KEY MATCHES KEY OF ACCOUNT AT INDEX 0 (MINT ACCOUNT)                                                                  |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT                                                                                                               |                                            |
|                          | C: MINT ACCOUNT'S MINT AUTHORITY EXISTS                                                                                                           |                                            |
|                          | C: MINT AUTHORITY IS A SIGNER ACCOUNT AT INDEX 2                                                                                                  |                                            |
|                          | C: MINT ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                                      |                                            |
|                          | C: DESTINATION ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                               |                                            |
|                          | E: EARLY RETURN (IF ZERO TRANSFER)                                                                                                                | P-ONLY                                     |
|                          | E: UPDATE DESTINATION ACCOUNT BALANCE                                                                                                             | P-ONLY: Swapped with successor             |
|                          | E: UPDATE MINT TOTAL SUPPLY                                                                                                                       |                                            |
| MintToChecked            | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 1 (DESTINATION ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                          |                                            |
|                          | C: DESTINATION ACCOUNT IS NOT FROZEN                                                                                                              |                                            |
|                          | C: DESTINATION ACCOUNT IS NOT NATIVE                                                                                                              |                                            |
|                          | C: DESTINATION ACCOUNT MINT KEY MATCHES KEY OF ACCOUNT AT INDEX 0 (MINT ACCOUNT)                                                                  |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT                                                                                                               |                                            |
|                          | C: EXPECTED DECIMALS PARAMETER MATCHES MINT ACCOUNT EXPECTED DECIMALS                                                                             |                                            |
|                          | C: MINT ACCOUNT'S MINT AUTHORITY EXISTS                                                                                                           |                                            |
|                          | C: MINT AUTHORITY IS A SIGNER ACCOUNT AT INDEX 2                                                                                                  |                                            |
|                          | C: MINT ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                                      |                                            |
|                          | C: DESTINATION ACCOUNT IS OWNED BY TOKEN PROGRAM (IF ZERO TRANSFER)                                                                               |                                            |
|                          | E: EARLY RETURN (IF ZERO TRANSFER)                                                                                                                | P-ONLY                                     |
|                          | E: UPDATE DESTINATION ACCOUNT BALANCE                                                                                                             | P-ONLY: Swapped with successor             |
|                          | E: UPDATE MINT TOTAL SUPPLY                                                                                                                       |                                            |
| FreezeAccount/           | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
| ThawAccount              | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: SOURCE ACCOUNT FROZENNESS DOES NOT MATCH TARGET FROZENNESS                                                                                     |                                            |
|                          | C: SOURCE ACCOUNT IS NOT NATIVE                                                                                                                   |                                            |
|                          | C: SOURCE ACCOUNT MINT KEY MATCHES KEY OF ACCOUNT AT INDEX 1 (MINT ACCOUNT)                                                                       |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT                                                                                                               |                                            |
|                          | C: MINT FREEZE AUTHORITY EXISTS                                                                                                                   |                                            |
|                          | C: MINT FREEZE AUTHORITY IS A SIGNER ACCOUNT AT INDEX 2                                                                                           |                                            |
|                          | E: UPDATE SOURCE ACCOUNT TO NEW TARGET FROZENNESS                                                                                                 |                                            |
| SyncNative               | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS OWNED BY TOKEN PROGRAM                                                                                  |                                            |
|                          | C: SOURCE ACCOUNT IS WELL-FORMED TOKEN ACCOUNT                                                                                                    |                                            |
|                          | C: SOURCE ACCOUNT IS NATIVE                                                                                                                       |                                            |
|                          | C: SOURCE ACCOUNT LAMPORTS IS SUFFICIENT FOR RENT-EXEMPTION                                                                                       |                                            |
|                          | C: SOURCE ACCOUNT RENT-EXEMPT LAMPORTS >= TOKEN AMOUNT                                                                                            |                                            |
|                          | E: SET SOURCE ACCOUNT TOKEN AMOUNT TO ITS RENT-EXEMPT LAMPORTS                                                                                    |                                            |
| Transfer                 | C: ACCOUNT ARITY >= 3                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: ACCOUNT AT INDEX 1 (DESTINATION ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                          | P-ONLY: Skip if self-transfer              |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: DESTINATION ACCOUNT IS NOT FROZEN                                                                                                              | P-ONLY: Skip if self-transfer              |
|                          | C: SOURCE TOKEN AMOUNT >= TRANSFER AMOUNT                                                                                                         |                                            |
|                          | C: SOURCE/DESTINATION ACCOUNT MINT KEY MATCHES                                                                                                    |                                            |
|                          | C: SOURCE ACCOUNT DELEGATE OR OWNER IS SIGNER AT ACCOUNT INDEX 2                                                                                  |                                            |
|                          | C: DELEGATED AMOUNT >= TRANSFER AMOUNT (IF DELEGATE IS SIGNER)                                                                                    |                                            |
|                          | E: DELEGATED AMOUNT IS DECREMENTED (IF DELEGATE IS SIGNER)                                                                                        | P-ONLY: Skip if self-transfer              |
|                          | E: DELEGATE ADDRESS IS CLEARED (IF DELEGATE IS SIGNER AND DELEGATED AMOUNT == TRANSFER AMOUNT)                                                    | P-ONLY: Skip if self-transfer              |
|                          | C: SOURCE/DESTINATION ACCOUNTS ARE OWNED BY TOKEN PROGRAM (IF SELF-TRANSFER OR ZERO TRANSFER)                                                     |                                            |
|                          | E: EARLY RETURN (IF SELF-TRANSFER)                                                                                                                | P-ONLY: Also early return if zero transfer |
|                          | E: DECREMENT SOURCE TOKEN AMOUNT, INCREMENT DESTINATION TOKEN AMOUNT                                                                              |                                            |
|                          | E: DECREMENT SOURCE TOKEN LAMPORTS, INCREMENT DESTINATION TOKEN LAMPORTS (IF MINT IS NATIVE)                                                      |                                            |
| TransferChecked          | C: ACCOUNT ARITY >= 4                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                               |                                            |
|                          | C: ACCOUNT AT INDEX 2 (DESTINATION ACCOUNT) IS WELL-FORMED TOKEN ACCOUNT                                                                          | P-ONLY: Skip if self-transfer              |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN                                                                                                                   |                                            |
|                          | C: DESTINATION ACCOUNT IS NOT FROZEN                                                                                                              | P-ONLY: Skip if self-transfer              |
|                          | C: SOURCE TOKEN AMOUNT >= TRANSFER AMOUNT                                                                                                         |                                            |
|                          | C: SOURCE/DESTINATION ACCOUNT MINT KEY MATCHES                                                                                                    |                                            |
|                          | C: SOURCE ACCOUNT MINT KEY MATCHES KEY OF ACCOUNT AT INDEX 1 (MINT ACCOUNT)                                                                       |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT                                                                                                               |                                            |
|                          | C: EXPECTED DECIMALS PARAMETER MATCHES MINT ACCOUNT EXPECTED DECIMALS                                                                             |                                            |
|                          | C: SOURCE ACCOUNT DELEGATE OR OWNER IS SIGNER AT ACCOUNT INDEX 3                                                                                  |                                            |
|                          | C: DELEGATED AMOUNT >= TRANSFER AMOUNT (IF DELEGATE IS SIGNER)                                                                                    |                                            |
|                          | E: DELEGATED AMOUNT IS DECREMENTED (IF DELEGATE IS SIGNER)                                                                                        | P-ONLY: Skip if self-transfer              |
|                          | E: DELEGATE ADDRESS IS CLEARED (IF DELEGATE IS SIGNER AND DELEGATED AMOUNT == TRANSFER AMOUNT)                                                    | P-ONLY: Skip if self-transfer              |
|                          | C: SOURCE/DESTINATION ACCOUNTS ARE OWNED BY TOKEN PROGRAM (IF SELF-TRANSFER OR ZERO TRANSFER)                                                     |                                            |
|                          | E: EARLY RETURN (IF SELF-TRANSFER)                                                                                                                | P-ONLY: Also early return if zero transfer |
|                          | E: DECREMENT SOURCE TOKEN AMOUNT, INCREMENT DESTINATION TOKEN AMOUNT                                                                              |                                            |
|                          | E: DECREMENT SOURCE TOKEN LAMPORTS, INCREMENT DESTINATION TOKEN LAMPORTS (IF MINT IS NATIVE)                                                      |                                            |
| SetAuthority             | C: ACCOUNT ARITY >= 2                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS A WELL-FORMED TOKEN ACCOUNT (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE)                                |                                            |
|                          | C: SOURCE ACCOUNT IS NOT FROZEN (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE)                                                                      |                                            |
|                          | C: AUTHORITY TYPE IS ACCOUNT OWNER OR ACCOUNT CLOSER (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE)                                                 |                                            |
|                          | C: SOURCE ACCOUNT OWNER IS A SIGNER ACCOUNT AT INDEX 1 (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE AND AUTHORITY TYPE IS ACCOUNT OWNER)           |                                            |
|                          | C: NEW ACCOUNT OWNER IS NON-NULL (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE AND AUTHORITY TYPE IS ACCOUNT OWNER)                                 |                                            |
|                          | E: RESET ACCOUNT DELEGATION STATUS, SET NEW ACCOUNT OWNER (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE AND AUTHORITY TYPE IS ACCOUNT OWNER)        |                                            |
|                          | E: RESET CLOSE ACCOUNT AUTHORITY (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE AND AUTHORITY TYPE IS ACCOUNT OWNER AND SOURCE ACCOUNT IS NATIVE)    |                                            |
|                          | C: SOURCE ACCOUNT CLOSER OR OWNER IS A SIGNER ACCOUNT AT INDEX 1 (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE AND AUTHORITY TYPE IS CLOSE ACCOUNT) |                                            |
|                          | E: UPDATE SOURCE ACCOUNT CLOSER AUTHORITY (IF DATA FIELD LENGTH IS TOKEN ACCOUNT SIZE AND AUTHORITY TYPE IS CLOSE ACCOUNT)                        |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS WELL-FORMED MINT (IF DATA LENGTH IS MINT SIZE)                                                          |                                            |
|                          | C: AUTHORITY TYPE IS EITHER MINT TOKENS OR FREEZE ACCOUNT (IF DATA LENGTH IS MINT SIZE)                                                           |                                            |
|                          | C: MINT AUTHORITY IS NON-NULL AND IS A SIGNER ACCOUNT AT INDEX 1 (IF DATA LENGTH IS MINT SIZE AND AUTHORITY TYPE IS MINT TOKENS)                  |                                            |
|                          | E: UPDATE MINT AUTHORITY (IF DATA LENGTH IS MINT SIZE AND AUTHORITY TYPE IS MINT AUTHORITY)                                                       |                                            |
|                          | C: FREEZE ACCOUNT AUTHORITY IS NON-NULL AND IS A SIGNER ACCOUNT AT INDEX 1 (IF DATA LENGTH IS MINT SIZE AND AUTHORITY TYPE IS FREEZE ACCOUNT)     |                                            |
|                          | E: UPDATE FREEZE ACCOUNT AUTHORITY (IF DATA LENGTH IS MINT SIZE AND AUTHORITY TYPE IS FREEZE ACCOUNT)                                             |                                            |
| GetAccountDataSize       | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (MINT ACCOUNT) IS OWNED BY TOKEN PROGRAM                                                                                    |                                            |
|                          | C: MINT ACCOUNT IS WELL-FORMED MINT                                                                                                               |                                            |
|                          | E: RETURN TOKEN ACCOUNT LENGTH CONSTANT                                                                                                           |                                            |
| AmountToUiAmount         | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS OWNED BY TOKEN PROGRAM                                                                                  |                                            |
|                          | C: SOURCE ACCOUNT IS WELL-FORMED MINT                                                                                                             |                                            |
|                          | E: RETURN UTF-8 RENDERING OF AMOUNT PARAMTER WITH MINT DECIMALS                                                                                   |                                            |
| UiAmountToAmount         | C: ACCOUNT ARITY >= 1                                                                                                                             |                                            |
|                          | C: ACCOUNT AT INDEX 0 (SOURCE ACCOUNT) IS OWNED BY TOKEN PROGRAM                                                                                  |                                            |
|                          | C: SOURCE ACCOUNT IS WELL-FORMED MINT                                                                                                             |                                            |
|                          | E: RETURN U64 AMOUNT FROM RENDERED UTF-8 AMOUNT AND MINT DECIMALS                                                                                 |                                            |

## Kompass Proofs

The results of the mechanical Kompass equivlanence proofs can be found in [this KaaS Vault (FIXME: Correct vault link to come)](https://kaas.runtimeverification.com/).
The proofs can be locally run by following the instructions listed in [VERIFICATION_GUIDE.md](https://github.com/runtimeverification/solana-token/blob/proofs/p-token/test-properties/VERIFICATION_GUIDE.md).

`VERIFICATION_GUIDE.md` also contains information about the cheatcodes used to set the appropriate symbolic state, as well as assumptions that are made as part of the solana domain, and limitations of the mechanical proofs.
