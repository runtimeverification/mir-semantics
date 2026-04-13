#![feature(portable_simd)]

use std::simd::prelude::*;

fn main() {
    // Splat a single value across all lanes
    let v = Simd::<i32, 4>::splat(7);
    let arr = v.to_array();

    assert!(arr[0] == 7);
    assert!(arr[1] == 7);
    assert!(arr[2] == 7);
    assert!(arr[3] == 7);
}
