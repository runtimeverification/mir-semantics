use std::num::NonZeroU8;

// Verify NonZero::checked_mul.
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
// NOTE: checked_mul returns Option<NonZeroU8>, which may hit the
// niche-cast blocker. This harness only tests the non-overflowing case
// where the return value goes through the transmute path.
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_10: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(10) };

fn main() {
    test_checked_mul_no_overflow();
}

fn test_checked_mul_no_overflow() {
    // 3 * 10 = 30, no overflow -- returns Some(NonZeroU8(30))
    let result = NZ_3.checked_mul(NZ_10);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 30);
}
