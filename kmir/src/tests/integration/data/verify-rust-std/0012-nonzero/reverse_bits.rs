#![feature(nonzero_bitwise)]

use std::num::NonZeroU8;

// Verify NonZeroU8::reverse_bits.
// Part 2 requirement: bit ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };   // 0b00000001
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };   // 0b00000101
const NZ_240: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(240) }; // 0b11110000

fn main() {
    test_reverse_bits();
}

fn test_reverse_bits() {
    assert!(NZ_1.reverse_bits().get() == 128);
    assert!(NZ_5.reverse_bits().get() == 160);
    assert!(NZ_240.reverse_bits().get() == 15);
}
