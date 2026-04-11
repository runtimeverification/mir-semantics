use std::num::NonZeroU8;

// Verify NonZero::saturating_mul (saturating multiplication).
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_10: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(10) };
const NZ_100: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(100) };

fn main() {
    test_saturating_mul();
}

fn test_saturating_mul() {
    // 3 * 10 = 30, no overflow
    let result = NZ_3.saturating_mul(NZ_10);
    assert!(result.get() == 30);

    // 100 * 10 = 1000, overflows u8 (max 255), saturates to 255
    let result = NZ_100.saturating_mul(NZ_10);
    assert!(result.get() == 255);
}
