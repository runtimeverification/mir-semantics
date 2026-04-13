// Harness for `Alignment::new_unchecked` (core::ptr::alignment)
//
// Verifies that Alignment::new_unchecked correctly creates alignment values
// from power-of-two usize values.

#![feature(ptr_alignment_type)]

use std::ptr::Alignment;

fn main() {
    let a1 = unsafe { Alignment::new_unchecked(1) };
    assert!(a1.as_usize() == 1);

    let a2 = unsafe { Alignment::new_unchecked(2) };
    assert!(a2.as_usize() == 2);

    let a4 = unsafe { Alignment::new_unchecked(4) };
    assert!(a4.as_usize() == 4);

    let a8 = unsafe { Alignment::new_unchecked(8) };
    assert!(a8.as_usize() == 8);
}
