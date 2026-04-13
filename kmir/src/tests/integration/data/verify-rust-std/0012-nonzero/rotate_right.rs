#![feature(nonzero_bitwise)]

use std::num::NonZeroU8;

// Verify NonZeroU8::rotate_right.
// Part 2 requirement: bit ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_2: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(2) };   // 0b00000010
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };   // 0b00000101
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };   // 0b00000011

fn main() {
    test_rotate_right();
}

fn test_rotate_right() {
    assert!(NZ_2.rotate_right(1).get() == 1);
    assert!(NZ_5.rotate_right(2).get() == 65);
    assert!(NZ_3.rotate_right(1).get() == 129);
}
