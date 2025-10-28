#![feature(core_intrinsics)]

// Negative test: assume(x < 10) then assert!(x > 10).
// With correct cheatcode semantics, this path is infeasible and the proof should fail.

use std::intrinsics::assume;

#[no_mangle]
pub fn check_assume_conflict(x: u64) {
    unsafe { assume(x < 10); }
    assert!(x > 10);
}

fn main() {}

