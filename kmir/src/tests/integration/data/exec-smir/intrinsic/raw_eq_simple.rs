#![feature(core_intrinsics)]

use std::intrinsics::raw_eq;

// NOTE: This test demonstrates the raw_eq intrinsic implementation.
// Known issue: Haskell backend produces more verbose symbolic execution output
// compared to LLVM backend due to different handling of symbolic branches.
// Both backends correctly implement the intrinsic but output format differs.

fn main() {
    let a = 42;
    let b = 42;
    
    // Test raw_eq intrinsic with identical values
    let result = unsafe { raw_eq(&a, &b) };
    
    // This assertion should pass as both values are identical
    assert!(result);
}