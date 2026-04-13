#![feature(nonzero_bitwise)]

use std::num::NonZeroU8;

// Verify NonZeroU8::from_le.
// Part 2 requirement: byte-order conversions.
// For u8, from_le is an identity operation.
// Construction uses const to bypass the niche-cast blocker.
const NZ_42: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(42) };

fn main() {
    test_from_le();
}

fn test_from_le() {
    let result = NonZeroU8::from_le(NZ_42);
    assert!(result.get() == 42);
}
