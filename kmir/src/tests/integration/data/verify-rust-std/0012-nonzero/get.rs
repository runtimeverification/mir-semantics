use std::num::{NonZeroI8, NonZeroU8};

// Verify NonZero::get for both unsigned and signed types.
// Construction uses const to bypass the niche-cast blocker.
const NZ_U8_1: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(1) };
const NZ_U8_42: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(42) };
const NZ_U8_255: NonZeroU8 = unsafe { NonZeroU8::new_unchecked(255) };
const NZ_I8_1: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(1) };
const NZ_I8_NEG1: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(-1) };
const NZ_I8_127: NonZeroI8 = unsafe { NonZeroI8::new_unchecked(127) };

fn main() {
    test_get_u8();
    test_get_i8();
}

fn test_get_u8() {
    assert!(NZ_U8_1.get() == 1);
    assert!(NZ_U8_42.get() == 42);
    assert!(NZ_U8_255.get() == 255);
}

fn test_get_i8() {
    assert!(NZ_I8_1.get() == 1);
    assert!(NZ_I8_NEG1.get() == -1);
    assert!(NZ_I8_127.get() == 127);
}
