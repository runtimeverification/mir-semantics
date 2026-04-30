#![feature(core_intrinsics)]
use std::intrinsics::saturating_sub;

fn main() {
    check_saturating_sub(0, 0);
}

fn check_saturating_sub(a: i32, b: i32) {
    if a <= b {
        assert_eq!(0, saturating_sub(a, b));
    } else {
        assert_eq!(a - b, saturating_sub(a, b));
    }
}
