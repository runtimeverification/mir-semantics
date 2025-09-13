#![feature(core_intrinsics)]

use std::intrinsics::raw_eq;

// NOTE: This test demonstrates the raw_eq intrinsic implementation.
// Known issue: Haskell backend produces more verbose symbolic execution output
// compared to LLVM backend due to different handling of symbolic branches.
// Both backends correctly implement the intrinsic but output format differs.

fn main() {
    let a = 42;
    let b = 42;
    
    // Test raw_eq intrinsic with identical values (both variables)
    let result = unsafe { raw_eq(&a, &b) };
    assert!(result);
    
    // TODO: need alloc to be supported in the semantics
    // // Test raw_eq with constant and variable (same type, same value)
    // let result_const_var = unsafe { raw_eq(&42, &a) };
    // assert!(result_const_var);
    
    // // Test raw_eq with constant and variable (same type, different value)
    // let c = 24;
    // let result_const_var_diff = unsafe { raw_eq(&42, &c) };
    // assert!(!result_const_var_diff);
}