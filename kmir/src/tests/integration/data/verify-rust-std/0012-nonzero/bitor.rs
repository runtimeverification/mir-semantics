use std::num::NonZeroU8;

// Verify NonZero bitwise OR operation.
// Part 2 requirement: bitor, bit ops.
// Construction uses const to bypass the niche-cast blocker.
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };   // 0b00000011
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };   // 0b00000101
const NZ_12: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(12) }; // 0b00001100

fn main() {
    test_bitor_basic();
    test_bitor_with_u8();
}

fn test_bitor_basic() {
    // NonZeroU8 | NonZeroU8 -> NonZeroU8
    let result = NZ_3 | NZ_5;
    assert!(result.get() == 7);  // 0b00000111

    let result2 = NZ_5 | NZ_12;
    assert!(result2.get() == 13); // 0b00001101
}

fn test_bitor_with_u8() {
    // NonZeroU8 | u8 -> NonZeroU8
    let result = NZ_3 | 4u8;
    assert!(result.get() == 7);  // 0b00000111

    let result2 = NZ_5 | 8u8;
    assert!(result2.get() == 13); // 0b00001101
}
