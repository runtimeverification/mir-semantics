#![feature(core_intrinsics)]

// Demonstrate and test the assume cheatcode semantics.
// The K semantics should add the condition `x < 100` as a path constraint,
// allowing the following assertion to be proven symbolically for all x.

use std::intrinsics::assume;

#[no_mangle]
pub fn check_assume(x: u64) {
    unsafe { assume(x < 100); }
    assert!(x < 100);
}

fn main() {}
