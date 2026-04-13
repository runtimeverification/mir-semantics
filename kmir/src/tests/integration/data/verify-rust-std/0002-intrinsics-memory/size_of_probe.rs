#![feature(core_intrinsics)]

use std::intrinsics;

fn main() {
    assert!(intrinsics::size_of::<u32>() == 4);
}
