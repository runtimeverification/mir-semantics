#![feature(portable_simd)]

use std::simd::prelude::*;

fn main() {
    let a = Simd::<i32, 4>::from_array([1, 2, 3, 4]);
    let b = Simd::<i32, 4>::from_array([1, 0, 3, 0]);

    // Lane-wise equality comparison
    let mask = a.simd_eq(b);

    assert!(mask.test(0)); // 1 == 1
    assert!(!mask.test(1)); // 2 != 0
    assert!(mask.test(2)); // 3 == 3
    assert!(!mask.test(3)); // 4 != 0
}
