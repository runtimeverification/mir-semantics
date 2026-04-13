// Harness for `Layout::from_size_align_unchecked` (core::alloc::layout)
//
// Verifies that Layout::from_size_align_unchecked correctly creates layouts
// from valid size and alignment values.

use std::alloc::Layout;

fn main() {
    // size 4, align 4
    let l1 = unsafe { Layout::from_size_align_unchecked(4, 4) };
    assert!(l1.size() == 4);
    assert!(l1.align() == 4);

    // size 0, align 1
    let l2 = unsafe { Layout::from_size_align_unchecked(0, 1) };
    assert!(l2.size() == 0);
    assert!(l2.align() == 1);

    // size 16, align 8
    let l3 = unsafe { Layout::from_size_align_unchecked(16, 8) };
    assert!(l3.size() == 16);
    assert!(l3.align() == 8);

    // size 1, align 1
    let l4 = unsafe { Layout::from_size_align_unchecked(1, 1) };
    assert!(l4.size() == 1);
    assert!(l4.align() == 1);
}
