// Harness for `Alignment::new` (core::ptr::alignment)
//
// Verifies that Alignment::new correctly validates power-of-two values.

#![feature(ptr_alignment_type)]

use std::ptr::Alignment;

fn main() {
    // Valid: 1 is a power of two
    let a1 = Alignment::new(1);
    assert!(a1.is_some());
    assert!(a1.unwrap().as_usize() == 1);

    // Valid: 2 is a power of two
    let a2 = Alignment::new(2);
    assert!(a2.is_some());
    assert!(a2.unwrap().as_usize() == 2);

    // Valid: 4 is a power of two
    let a4 = Alignment::new(4);
    assert!(a4.is_some());
    assert!(a4.unwrap().as_usize() == 4);

    // Valid: 8 is a power of two
    let a8 = Alignment::new(8);
    assert!(a8.is_some());
    assert!(a8.unwrap().as_usize() == 8);
}
