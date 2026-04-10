use std::num::{NonZeroI16, NonZeroI32, NonZeroI8, NonZeroU16, NonZeroU32, NonZeroU8};

fn main() {
    verify_nonzero_from_u8_to_u16(NonZeroU8::new(1).unwrap());
    verify_nonzero_from_u8_to_u32(NonZeroU8::new(1).unwrap());
    verify_nonzero_from_i8_to_i16(NonZeroI8::new(1).unwrap());
    verify_nonzero_from_i8_to_i32(NonZeroI8::new(1).unwrap());
}

fn verify_nonzero_from_u8_to_u16(value: NonZeroU8) {
    let result: NonZeroU16 = value.into();
    assert!(result.get() == value.get() as u16);
}

fn verify_nonzero_from_u8_to_u32(value: NonZeroU8) {
    let result: NonZeroU32 = value.into();
    assert!(result.get() == value.get() as u32);
}

fn verify_nonzero_from_i8_to_i16(value: NonZeroI8) {
    let result: NonZeroI16 = value.into();
    assert!(result.get() == value.get() as i16);
}

fn verify_nonzero_from_i8_to_i32(value: NonZeroI8) {
    let result: NonZeroI32 = value.into();
    assert!(result.get() == value.get() as i32);
}
