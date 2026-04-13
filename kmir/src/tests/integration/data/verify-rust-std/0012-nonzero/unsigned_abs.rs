use std::num::{NonZeroI8, NonZeroU8};

// Verify NonZeroI8::unsigned_abs.
// Part 2 requirement: signed-only ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };
const NZ_NEG_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-5) };

fn main() {
    let positive: NonZeroU8 = NZ_POS_5.unsigned_abs();
    assert!(positive.get() == 5);

    let negative: NonZeroU8 = NZ_NEG_5.unsigned_abs();
    assert!(negative.get() == 5);
}
