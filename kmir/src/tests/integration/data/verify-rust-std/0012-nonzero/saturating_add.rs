use std::num::NonZeroU8;

// Verify NonZero::saturating_add.
// Part 2 requirement: arithmetic.
// Construction uses const to bypass the niche-cast blocker.
const NZ_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_100: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(100) };
const NZ_250: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(250) };

fn main() {
    test_saturating_add();
}

fn test_saturating_add() {
    // 1 + 1 = 2, no saturation
    let result = NZ_1.saturating_add(1);
    assert!(result.get() == 2);

    // 100 + 50 = 150, no saturation
    let result = NZ_100.saturating_add(50);
    assert!(result.get() == 150);

    // 250 + 10 = 260, saturates to 255
    let result = NZ_250.saturating_add(10);
    assert!(result.get() == 255);
}
