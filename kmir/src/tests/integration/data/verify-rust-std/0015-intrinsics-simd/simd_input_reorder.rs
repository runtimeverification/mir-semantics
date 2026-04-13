#![feature(portable_simd)]

use std::simd::prelude::*;

fn main() {
    let input = [3_i32, 6, 9, 12];
    let staged = [input[3], input[1], input[2] - input[0], input[0] + input[1]];

    let vector = Simd::<i32, 4>::from_array(staged);
    let result = vector.to_array();

    assert!(result[0] == 12);
    assert!(result[1] == 6);
    assert!(result[2] == 6);
    assert!(result[3] == 9);
}
