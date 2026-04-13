#![feature(portable_simd)]

use std::simd::prelude::*;

fn main() {
    let a = Simd::<i32, 4>::from_array([1, 2, 3, 4]);
    let b = Simd::<i32, 4>::from_array([10, 20, 30, 40]);
    let c = a + b;
    let result = c.to_array();

    assert!(result[0] == 11);
    assert!(result[1] == 22);
    assert!(result[2] == 33);
    assert!(result[3] == 44);
}
