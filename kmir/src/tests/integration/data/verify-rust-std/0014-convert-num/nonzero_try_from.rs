use std::convert::TryFrom;
use std::num::{NonZeroI16, NonZeroI8, NonZeroU16, NonZeroU8};

fn main() {
    verify_nonzero_try_from_u16_to_u8(NonZeroU16::new(1).unwrap());
    verify_nonzero_try_from_i16_to_i8(NonZeroI16::new(1).unwrap());
    verify_nonzero_try_from_u8_to_i8(NonZeroU8::new(1).unwrap());
    verify_nonzero_try_from_i8_to_u8(NonZeroI8::new(1).unwrap());
}

fn verify_nonzero_try_from_u16_to_u8(value: NonZeroU16) {
    match NonZeroU8::try_from(value) {
        Ok(result) => assert!(result.get() == value.get() as u8),
        Err(_) => assert!(value.get() > u8::MAX as u16),
    }
}

fn verify_nonzero_try_from_i16_to_i8(value: NonZeroI16) {
    match NonZeroI8::try_from(value) {
        Ok(result) => assert!(result.get() == value.get() as i8),
        Err(_) => assert!(value.get() > i8::MAX as i16 || value.get() < i8::MIN as i16),
    }
}

fn verify_nonzero_try_from_u8_to_i8(value: NonZeroU8) {
    match NonZeroI8::try_from(value) {
        Ok(result) => assert!(result.get() == value.get() as i8),
        Err(_) => assert!(value.get() > i8::MAX as u8),
    }
}

fn verify_nonzero_try_from_i8_to_u8(value: NonZeroI8) {
    match NonZeroU8::try_from(value) {
        Ok(result) => assert!(result.get() == value.get() as u8),
        Err(_) => assert!(value.get() < 0),
    }
}

