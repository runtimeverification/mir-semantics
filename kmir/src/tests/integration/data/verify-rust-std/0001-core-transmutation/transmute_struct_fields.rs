//! Proof harnesses for transmute with repr(transparent) structs.
//! Exercises the transparent wrapper rules: T -> Wrapper(T) and Wrapper(T) -> T.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

#[repr(transparent)]
struct Meters(u32);

fn transmute_u32_to_meters() {
    let x: u32 = 1000;
    let m: Meters = unsafe { transmute::<u32, Meters>(x) };
    assert!(m.0 == 1000);
}

fn transmute_meters_to_u32() {
    let m = Meters(500);
    let x: u32 = unsafe { transmute::<Meters, u32>(m) };
    assert!(x == 500);
}

#[repr(transparent)]
struct NonZeroLikeU64(u64);

fn transmute_u64_to_wrapper() {
    let x: u64 = 42;
    let nz: NonZeroLikeU64 = unsafe { transmute::<u64, NonZeroLikeU64>(x) };
    assert!(nz.0 == 42);
}

fn transmute_wrapper_to_u64() {
    let nz = NonZeroLikeU64(99);
    let y: u64 = unsafe { transmute::<NonZeroLikeU64, u64>(nz) };
    assert!(y == 99);
}

#[repr(transparent)]
struct WrapperU8(u8);

fn transmute_u8_roundtrip_through_wrapper() {
    let x: u8 = 200;
    let w: WrapperU8 = unsafe { transmute::<u8, WrapperU8>(x) };
    let y: u8 = unsafe { transmute::<WrapperU8, u8>(w) };
    assert!(x == y);
}

fn main() {
    transmute_u32_to_meters();
    transmute_meters_to_u32();
    transmute_u64_to_wrapper();
    transmute_wrapper_to_u64();
    transmute_u8_roundtrip_through_wrapper();
}
