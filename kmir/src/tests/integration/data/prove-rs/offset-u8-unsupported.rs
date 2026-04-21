// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT

// https://github.com/model-checking/kani/blob/main/tests/expected/offset-u8-fail/main.rs

// Checks that the pointer computed with `offset` causes a failure if it's
// dereferenced outside the object bounds
#![feature(core_intrinsics)]
use std::intrinsics::offset;

fn main() {
    test_offset();
}

// #[kani::proof]
fn test_offset() {
    let s: &str = "123";
    let ptr: *const u8 = s.as_ptr();

    unsafe {
        let x = *offset(ptr, 3isize) as char;
    }
}
