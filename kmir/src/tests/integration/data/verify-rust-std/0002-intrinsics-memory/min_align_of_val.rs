#![feature(core_intrinsics)]

use std::intrinsics;

#[repr(align(32))]
struct Align32(u64);

fn main() {
    let value = Align32(99);
    let align = unsafe { intrinsics::min_align_of_val(&value) };

    assert!(align == 32);
    assert!(value.0 == 99);
}
