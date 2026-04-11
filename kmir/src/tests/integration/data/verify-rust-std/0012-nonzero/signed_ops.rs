use std::num::NonZeroI8;

// Verify signed-only NonZero operations.
// Part 2 requirement: signed-only ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };
const NZ_NEG_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-5) };
const NZ_POS_1: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(1) };
const NZ_NEG_1: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-1) };

fn main() {
    test_is_positive();
    test_is_negative();
}

fn test_is_positive() {
    assert!(NZ_POS_5.is_positive());
    assert!(!NZ_NEG_5.is_positive());
    assert!(NZ_POS_1.is_positive());
    assert!(!NZ_NEG_1.is_positive());
}

fn test_is_negative() {
    assert!(!NZ_POS_5.is_negative());
    assert!(NZ_NEG_5.is_negative());
    assert!(!NZ_POS_1.is_negative());
    assert!(NZ_NEG_1.is_negative());
}

// test_signum removed: signum not available on this nightly
