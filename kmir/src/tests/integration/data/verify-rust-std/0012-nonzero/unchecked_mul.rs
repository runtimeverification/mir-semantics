#![feature(nonzero_ops)]

use std::num::NonZeroU8;

// Verify NonZero::unchecked_mul.
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_10: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(10) };

fn main() {
    test_unchecked_mul();
}

fn test_unchecked_mul() {
    // 3 * 10 = 30
    let result = unsafe { NZ_3.unchecked_mul(NZ_10) };
    assert!(result.get() == 30);
}
