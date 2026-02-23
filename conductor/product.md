# Product Guide

## Initial Concept
MIR Semantics provides a K Framework-based formal semantics for Rust's Stable MIR,
enabling symbolic execution and formal verification of Rust programs.

## Vision
MIR Semantics is an infrastructure layer for formal Rust verification pipelines.
It provides audit-grade reasoning at the MIR level through symbolic execution and
reachability proofs, serving as the foundational engine that verification toolchains
build upon.

## Core Capabilities

### 1. Complete K-Based Formal Semantics of Stable MIR
The project defines a mathematically rigorous formal semantics for Rust's Stable MIR
using the K Framework. Unlike heuristic-based analysis tools, this enables proofs
grounded in a complete semantic model — covering control flow, type systems, memory
operations, and runtime behavior.

### 2. End-to-End Verification Pipeline
A seamless pipeline transforms Rust source code into verifiable artifacts:
- **Rust source** → `stable-mir-json` extracts **SMIR JSON**
- SMIR JSON → Python layer (`kmir`) transforms into **K terms**
- K terms → K Framework performs **symbolic execution and reachability proofs**

The `kmir` Python CLI orchestrates this entire flow, exposing commands like
`prove-rs` for direct source-to-proof workflows.

### 3. Extensible Domain-Specific Verification
An intrinsic and cheatcode system allows the semantics to be extended for
domain-specific verification targets. Current extensions support Solana SPL
token program verification (e.g., multisig cheatcodes, rent calculations),
with the architecture designed for additional blockchain and systems-level targets.

## Current Focus
- **Feature development:** Expanding MIR coverage — new types, operations,
  intrinsics, and casts to handle a broader set of Rust programs.
- **Stabilization:** Improving proof reliability, resolving edge cases in
  symbolic execution, and increasing integration test coverage.

## Stakeholders
- Runtime Verification, Inc. — primary development team
- Polkadot and Solana ecosystems — verification pipeline consumers
- K Framework community — formal methods researchers and contributors
