use std::num::NonZeroU8;

// Verify NonZero::checked_pow (exponentiation with overflow check).
// Part 2 requirement: arithmetic, powers.
// Construction uses const to bypass the niche-cast blocker.
const NZ_2: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(2) };
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };

fn main() {
    test_checked_pow();
}

fn test_checked_pow() {
    // 2^0 = 1, no overflow
    let result = NZ_2.checked_pow(0);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 1);

    // 2^3 = 8, no overflow
    let result = NZ_2.checked_pow(3);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 8);

    // 3^2 = 9, no overflow
    let result = NZ_3.checked_pow(2);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 9);

    // 5^1 = 5, no overflow
    let result = NZ_5.checked_pow(1);
    assert!(result.is_some());
    assert!(result.unwrap().get() == 5);
}
