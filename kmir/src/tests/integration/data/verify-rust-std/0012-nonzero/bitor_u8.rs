use std::num::NonZeroU8;

// Verify the third BitOr impl: u8 | NonZeroU8 -> NonZeroU8.
// Construction uses const to bypass the niche-cast blocker.
const NZ_3: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(3) };   // 0b00000011
const NZ_5: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(5) };   // 0b00000101
const NZ_12: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(12) }; // 0b00001100

fn main() {
    test_bitor_u8_lhs();
}

fn test_bitor_u8_lhs() {
    // u8 | NonZeroU8 -> NonZeroU8
    let result = 0u8 | NZ_3;
    assert!(result.get() == 3); // 0b00000011

    let result2 = 8u8 | NZ_5;
    assert!(result2.get() == 13); // 0b00001101

    let result3 = 1u8 | NZ_12;
    assert!(result3.get() == 13); // 0b00001101
}
