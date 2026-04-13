use std::num::NonZeroI8;

// Verify NonZeroI8 absolute-value operations.
// Part 2 requirement: signed-only ops.
// Construction uses const to bypass the niche-cast blocker.
// NOTE: checked_abs overflow-to-None is omitted because niche-encoded None
// remains blocked; this harness covers the non-overflowing path.
const NZ_NEG_1: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-1) };
const NZ_NEG_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-5) };
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };

fn main() {
    assert!(NZ_NEG_5.abs().get() == 5);

    let result = NZ_NEG_1.checked_abs();
    assert!(result.is_some());
    assert!(result.unwrap().get() == 1);

    let (value, overflow) = NZ_NEG_1.overflowing_abs();
    assert!(value.get() == 1);
    assert!(!overflow);

    assert!(NZ_POS_5.saturating_abs().get() == 5);
    assert!(NZ_NEG_5.wrapping_abs().get() == 5);
    assert!(NZ_NEG_5.unsigned_abs().get() == 5);
}
