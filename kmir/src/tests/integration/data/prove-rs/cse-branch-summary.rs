#![feature(core_intrinsics)]

use std::intrinsics::assume;

fn classify(x: u32) -> u32 {
    if x > 10 {
        1
    } else {
        0
    }
}

#[no_mangle]
pub fn partial_caller0(x: u32) {
    unsafe { assume(x > 20); }
    let result = classify(x);
    assert!(result == 1);
}

#[no_mangle]
pub fn partial_caller1(x: u32) {
    unsafe { assume(x > 10); }
    let result = classify(x);
    assert!(result == 1);
}

#[no_mangle]
pub fn partial_caller2(x: u32) {
    unsafe { assume(x <= 10); }
    let result = classify(x);
    assert!(result == 0);
}

#[no_mangle]
pub fn caller(x: u32) {
    let result = classify(x);
    if x > 10 {
        assert!(result == 1);
    } else {
        assert!(result == 0);
    }
}

fn main() {}
