// Harness for `Layout::from_size_align` (core::alloc::layout)
//
// Verifies that Layout::from_size_align correctly validates and creates layouts.

use std::alloc::Layout;

fn main() {
    // Valid: size 4, align 4
    let l1 = Layout::from_size_align(4, 4).unwrap();
    assert!(l1.size() == 4);
    assert!(l1.align() == 4);

    // Valid: size 0, align 1
    let l2 = Layout::from_size_align(0, 1).unwrap();
    assert!(l2.size() == 0);
    assert!(l2.align() == 1);
}
