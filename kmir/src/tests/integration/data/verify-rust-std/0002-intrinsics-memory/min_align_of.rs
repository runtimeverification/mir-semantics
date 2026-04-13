#![feature(core_intrinsics)]

use std::intrinsics;

#[repr(align(16))]
struct Align16(u8);

fn main() {
    let align_u8 = intrinsics::min_align_of::<u8>();
    let align_custom = intrinsics::min_align_of::<Align16>();

    assert!(align_u8 == 1);
    assert!(align_custom == 16);
}
