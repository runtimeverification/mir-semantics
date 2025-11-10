#![feature(core_intrinsics)]
use std::intrinsics;

fn main() {
    intrinsics::cold_path();
    let b = true;
    intrinsics::likely(b);
    intrinsics::unlikely(b);
}
