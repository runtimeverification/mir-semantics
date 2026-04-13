use std::num::NonZeroU8;

// Verify NonZero::saturating_pow.
// Part 2 requirement: arithmetic, powers.
// Construction uses const to bypass the niche-cast blocker.
const NZ_2: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(2) };
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };
const NZ_MAX: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(u8::MAX) };

fn main() {
    test_saturating_pow();
}

fn test_saturating_pow() {
    // 2^3 = 8
    let result = NZ_2.saturating_pow(3);
    assert!(result.get() == 8);

    // 3^2 = 9
    let result = NZ_3.saturating_pow(2);
    assert!(result.get() == 9);

    // 5^1 = 5
    let result = NZ_5.saturating_pow(1);
    assert!(result.get() == 5);

    // 255^1 = 255
    let result = NZ_MAX.saturating_pow(1);
    assert!(result.get() == 255);
}
