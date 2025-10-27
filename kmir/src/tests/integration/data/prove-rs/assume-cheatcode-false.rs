#![feature(core_intrinsics)]

// Test case: assume(false) should make the path infeasible.
// If assume is not honored, the subsequent assert!(false) would fail the proof.

use std::intrinsics::assume;

fn main() {
    unsafe { assume(false); }
    // Unreachable if the cheatcode is effective.
    assert!(false);
}

