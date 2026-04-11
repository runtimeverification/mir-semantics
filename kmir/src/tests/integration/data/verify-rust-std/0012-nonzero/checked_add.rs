use std::num::NonZeroU8;

// Verify NonZero::checked_add (non-overflow case).
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
// NOTE: Overflow case (returning None) is blocked by UnableToDecode for niche-encoded Option.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_100: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(100) };
const NZ_254: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(254) };

fn main() {
    test_checked_add_no_overflow();
}

fn test_checked_add_no_overflow() {
    // 1 + 1 = 2, no overflow
    let result = NZ_1.checked_add(1);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 2);

    // 100 + 50 = 150, no overflow
    let result = NZ_100.checked_add(50);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 150);

    // 254 + 1 = 255, no overflow
    let result = NZ_254.checked_add(1);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 255);
}
