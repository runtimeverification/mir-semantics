#![feature(portable_simd)]

use std::simd::prelude::*;

fn main() {
    let a = Simd::<i32, 4>::from_array([2, 3, 4, 5]);
    let b = Simd::<i32, 4>::from_array([10, 10, 10, 10]);
    let c = a * b;
    let result = c.to_array();

    assert!(result[0] == 20);
    assert!(result[1] == 30);
    assert!(result[2] == 40);
    assert!(result[3] == 50);
}
