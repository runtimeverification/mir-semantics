use std::num::NonZeroU8;

// Verify NonZeroU8::checked_next_power_of_two (non-overflow cases).
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };
const NZ_17: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(17) };

fn main() {
    test_checked_next_power_of_two();
}

fn test_checked_next_power_of_two() {
    let result = NZ_1.checked_next_power_of_two();
    assert!(result.is_some());
    assert!(result.unwrap().get() == 1);

    let result = NZ_3.checked_next_power_of_two();
    assert!(result.is_some());
    assert!(result.unwrap().get() == 4);

    let result = NZ_5.checked_next_power_of_two();
    assert!(result.is_some());
    assert!(result.unwrap().get() == 8);

    let result = NZ_17.checked_next_power_of_two();
    assert!(result.is_some());
    assert!(result.unwrap().get() == 32);
}
