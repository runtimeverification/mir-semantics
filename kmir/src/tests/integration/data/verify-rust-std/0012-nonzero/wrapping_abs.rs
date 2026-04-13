use std::num::NonZeroI8;

// Verify NonZeroI8::wrapping_abs.
// Part 2 requirement: signed-only ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };
const NZ_NEG_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-5) };

fn main() {
    assert!(NZ_POS_5.wrapping_abs().get() == 5);
    assert!(NZ_NEG_5.wrapping_abs().get() == 5);
}
