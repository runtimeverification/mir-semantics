#![feature(num_midpoint)]

use std::num::NonZeroU8;

// Verify NonZeroU8::midpoint.
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_2: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(2) };
const NZ_4: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(4) };

fn main() {
    test_midpoint();
}

fn test_midpoint() {
    // midpoint(1, 4) = 2
    let result = NZ_1.midpoint(NZ_4);
    assert!(result.get() == 2);

    // midpoint(1, 2) = 1
    let result = NZ_1.midpoint(NZ_2);
    assert!(result.get() == 1);
}
