// Harness for `align_offset` (core::ptr)
//
// Verifies that an already aligned pointer reports zero offset.

use std::mem::align_of;

fn main() {
    let data = [1u32, 2, 3, 4];
    let ptr = data.as_ptr();
    let offset = ptr.align_offset(align_of::<u32>());

    assert!(offset == 0);
}
