#![feature(nonzero_ops)]

use std::num::NonZeroU8;

// Verify NonZero::unchecked_add.
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_100: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(100) };
const NZ_254: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(254) };

fn main() {
    test_unchecked_add();
}

fn test_unchecked_add() {
    // 1 + 1 = 2
    let result = unsafe { NZ_1.unchecked_add(1) };
    assert!(result.get() == 2);

    // 100 + 50 = 150
    let result = unsafe { NZ_100.unchecked_add(50) };
    assert!(result.get() == 150);

    // 254 + 1 = 255
    let result = unsafe { NZ_254.unchecked_add(1) };
    assert!(result.get() == 255);
}
