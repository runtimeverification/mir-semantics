#![feature(maybe_uninit_write_slice)]

// Harness for `MaybeUninit<T>::copy_from_slice` (core::mem::maybe_uninit)
//
// Verifies that copying a slice into uninitialized storage yields initialized data.

use std::mem::MaybeUninit;

fn main() {
    let src = [10u16, 20, 30, 40];
    let mut dst = [MaybeUninit::<u16>::uninit(); 4];

    let written = MaybeUninit::copy_from_slice(&mut dst, &src);
    assert!(written[0] == 10);
    assert!(written[1] == 20);
    assert!(written[3] == 40);
}
