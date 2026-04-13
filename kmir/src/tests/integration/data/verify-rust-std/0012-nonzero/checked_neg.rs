use std::num::NonZeroI8;

// Verify NonZeroI8 negation operations.
// Part 2 requirement: signed-only ops.
// Construction uses const to bypass the niche-cast blocker.
// NOTE: checked_neg overflow-to-None is omitted because niche-encoded None
// remains blocked; this harness covers the non-overflowing path.
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };

fn main() {
    let result = NZ_POS_5.checked_neg();
    assert!(result.is_some());
    assert!(result.unwrap().get() == -5);

    let (value, overflow) = NZ_POS_5.overflowing_neg();
    assert!(value.get() == -5);
    assert!(!overflow);

    assert!(NZ_POS_5.wrapping_neg().get() == -5);
}
