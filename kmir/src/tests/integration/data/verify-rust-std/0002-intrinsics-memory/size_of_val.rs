#![feature(core_intrinsics)]

use std::intrinsics;

fn main() {
    let data = [10u16, 20u16, 30u16];
    let slice: &[u16] = &data;

    let size = unsafe { intrinsics::size_of_val(slice) };

    assert!(size == 3 * std::mem::size_of::<u16>());
}
