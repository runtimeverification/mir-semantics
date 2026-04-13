#![feature(nonzero_bitwise)]

use std::num::NonZeroU8;

// Verify NonZeroU8::rotate_left.
// Part 2 requirement: bit ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };   // 0b00000001
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };   // 0b00000101
const NZ_129: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(129) }; // 0b10000001

fn main() {
    test_rotate_left();
}

fn test_rotate_left() {
    assert!(NZ_1.rotate_left(1).get() == 2);
    assert!(NZ_5.rotate_left(3).get() == 40);
    assert!(NZ_129.rotate_left(1).get() == 3);
}
