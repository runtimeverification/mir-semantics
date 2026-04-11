use std::num::NonZeroU8;

// Verify NonZero::leading_zeros and NonZero::trailing_zeros.
// Part 2 requirement: bit ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };     // 0b00000001
const NZ_128: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(128) }; // 0b10000000
const NZ_255: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(255) }; // 0b11111111
const NZ_16: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(16) };   // 0b00010000

fn main() {
    test_leading_zeros();
    test_trailing_zeros();
}

fn test_leading_zeros() {
    assert!(NZ_1.leading_zeros() == 7);
    assert!(NZ_128.leading_zeros() == 0);
    assert!(NZ_255.leading_zeros() == 0);
    assert!(NZ_16.leading_zeros() == 3);
}

fn test_trailing_zeros() {
    assert!(NZ_1.trailing_zeros() == 0);
    assert!(NZ_128.trailing_zeros() == 7);
    assert!(NZ_255.trailing_zeros() == 0);
    assert!(NZ_16.trailing_zeros() == 4);
}
