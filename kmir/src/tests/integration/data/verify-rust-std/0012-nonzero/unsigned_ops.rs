use std::num::NonZeroU8;

// Verify unsigned-only NonZero operations.
// Part 2 requirement: unsigned-only ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_2: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(2) };
const NZ_7: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(7) };
const NZ_128: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(128) };

fn main() {
    test_is_power_of_two();
    test_checked_log2();
}

fn test_is_power_of_two() {
    assert!(NZ_1.is_power_of_two());
    assert!(NZ_2.is_power_of_two());
    assert!(!NZ_7.is_power_of_two());
    assert!(NZ_128.is_power_of_two());
}

fn test_checked_log2() {
    // ilog2 is available on all nonzero unsigned types
    assert!(NZ_1.ilog2() == 0);
    assert!(NZ_2.ilog2() == 1);
    assert!(NZ_128.ilog2() == 7);
}
