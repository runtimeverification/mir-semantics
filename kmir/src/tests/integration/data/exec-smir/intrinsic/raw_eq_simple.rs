#![feature(core_intrinsics)]

use std::intrinsics::raw_eq;

fn main() {
    let a = 42;
    let b = 42;
    
    // This will get stuck at the raw_eq intrinsic call
    let result = unsafe { raw_eq(&a, &b) };
    
    // This line won't be reached without the intrinsic implementation
    assert!(result);
}