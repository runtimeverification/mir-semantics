use std::num::NonZeroI8;

// Verify NonZeroI8::saturating_abs.
// Part 2 requirement: signed-only ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };
const NZ_MIN: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(i8::MIN) };

fn main() {
    assert!(NZ_POS_5.saturating_abs().get() == 5);
    assert!(NZ_MIN.saturating_abs().get() == i8::MAX);
}
