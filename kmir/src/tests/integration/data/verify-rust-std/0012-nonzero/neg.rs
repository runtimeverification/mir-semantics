use std::num::NonZeroI8;

// Verify Neg for NonZeroI8.
// Part 2 requirement: negation.
// Construction uses const to bypass the niche-cast blocker.
const NZ_POS_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(5) };
const NZ_NEG_5: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-5) };

fn main() {
    test_neg();
}

fn test_neg() {
    // -5 negated is 5
    let result = -NZ_NEG_5;
    assert!(result.get() == 5);

    // 5 negated is -5
    let result = -NZ_POS_5;
    assert!(result.get() == -5);
}
