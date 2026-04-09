use std::mem::transmute;
use std::num::NonZeroU8;

#[repr(transparent)]
struct WrapU8(u8);

fn main() {
    part1_transmute_wrapper_u8();
    part1_transmute_option_nonzero_u8();
}

fn part1_transmute_wrapper_u8() {
    let wrapped: WrapU8 = unsafe { transmute::<u8, WrapU8>(1u8) };
    assert!(wrapped.0 == 1u8);
}

fn part1_transmute_option_nonzero_u8() {
    let value = 1u8;
    assert!(value != 0u8);

    let wrapped: Option<NonZeroU8> = unsafe { transmute::<u8, Option<NonZeroU8>>(value) };
    assert!(wrapped.is_some());
    assert!(wrapped.unwrap().get() == value);
}
