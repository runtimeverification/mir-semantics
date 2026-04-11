use std::num::NonZeroU8;

// Verify NonZero::min and NonZero::max.
// Part 2 requirement: max, min, clamp.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_42: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(42) };
const NZ_255: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(255) };

fn main() {
    test_min();
    test_max();
}

fn test_min() {
    let a = NZ_1;
    let b = NZ_42;
    let result = a.min(b);
    assert!(result.get() == 1);

    let result2 = b.min(NZ_255);
    assert!(result2.get() == 42);
}

fn test_max() {
    let a = NZ_1;
    let b = NZ_42;
    let result = a.max(b);
    assert!(result.get() == 42);

    let result2 = b.max(NZ_255);
    assert!(result2.get() == 255);
}
