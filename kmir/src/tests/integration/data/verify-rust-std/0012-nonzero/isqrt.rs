use std::num::NonZeroU8;

// Verify NonZeroU8::isqrt.
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_4: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(4) };
const NZ_15: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(15) };

fn main() {
    test_isqrt();
}

fn test_isqrt() {
    assert!(NZ_1.isqrt().get() == 1);
    assert!(NZ_3.isqrt().get() == 1);
    assert!(NZ_4.isqrt().get() == 2);
    assert!(NZ_15.isqrt().get() == 3);
}
