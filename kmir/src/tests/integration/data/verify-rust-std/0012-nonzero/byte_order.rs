#![feature(nonzero_bitwise)]

use std::num::NonZeroU8;

// Verify NonZero byte-order conversions.
// Part 2 requirement: byte-order conversions.
// For u8, to_be/to_le/swap_bytes are identity operations.
// Construction uses const to bypass the niche-cast blocker.
const NZ_42: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(42) };

fn main() {
    test_to_be();
    test_to_le();
    test_swap_bytes();
}

fn test_to_be() {
    // For single-byte types, to_be is identity
    let result = NZ_42.to_be();
    assert!(result.get() == 42);
}

fn test_to_le() {
    // For single-byte types, to_le is identity
    let result = NZ_42.to_le();
    assert!(result.get() == 42);
}

fn test_swap_bytes() {
    // For single-byte types, swap_bytes is identity
    let result = NZ_42.swap_bytes();
    assert!(result.get() == 42);
}
