#![feature(core_intrinsics)]

use std::intrinsics;

fn main() {
    let t = intrinsics::likely(true);
    let f = intrinsics::unlikely(false);

    assert!(t);
    assert!(!f);

    let likely_branch = if intrinsics::likely(3 < 5) { 7 } else { 9 };
    let unlikely_branch = if intrinsics::unlikely(2 > 10) { 11 } else { 13 };

    assert!(likely_branch == 7);
    assert!(unlikely_branch == 13);
}
