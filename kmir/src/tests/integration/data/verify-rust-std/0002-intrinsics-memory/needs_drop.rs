#![feature(core_intrinsics)]

use std::intrinsics;

struct Droppy;

impl Drop for Droppy {
    fn drop(&mut self) {}
}

fn main() {
    let plain_needs_drop = intrinsics::needs_drop::<u32>();
    let droppy_needs_drop = intrinsics::needs_drop::<Droppy>();

    assert!(!plain_needs_drop);
    assert!(droppy_needs_drop);
}
