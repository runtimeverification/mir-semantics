#![feature(pointer_is_aligned_to)]

// Harness for `is_aligned_to` (core::const_ptr)
//
// Tests that const pointer alignment checks work correctly.

fn main() {
    let val: u64 = 0x1234;
    let ptr = &val as *const u64;

    // A u64 reference should be aligned to at least 8
    assert!(ptr.is_aligned());

    // Any pointer is aligned to 1
    assert!(ptr.is_aligned_to(1));
}
