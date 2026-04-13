#![feature(portable_simd)]

use std::simd::prelude::*;

fn main() {
    let left = [5_i32, 10, 15, 20];
    let right = [50_i32, 100, 150, 200];
    let pick_left = [true, false, true, false];

    let staged = [
        if pick_left[0] { left[0] } else { right[0] },
        if pick_left[1] { left[1] } else { right[1] },
        if pick_left[2] { left[2] } else { right[2] },
        if pick_left[3] { left[3] } else { right[3] },
    ];

    let vector = Simd::<i32, 4>::from_array(staged);
    let result = vector.to_array();

    assert!(result[0] == 5);
    assert!(result[1] == 100);
    assert!(result[2] == 15);
    assert!(result[3] == 200);
}
