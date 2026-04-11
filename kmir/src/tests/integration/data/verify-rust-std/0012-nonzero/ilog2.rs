use std::num::NonZeroU8;

// Verify NonZero::ilog2 (integer log base 2).
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_2: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(2) };
const NZ_8: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(8) };
const NZ_255: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(255) };

fn main() {
    test_ilog2();
}

fn test_ilog2() {
    assert!(NZ_1.ilog2() == 0);
    assert!(NZ_2.ilog2() == 1);
    assert!(NZ_8.ilog2() == 3);
    assert!(NZ_255.ilog2() == 7);
}
