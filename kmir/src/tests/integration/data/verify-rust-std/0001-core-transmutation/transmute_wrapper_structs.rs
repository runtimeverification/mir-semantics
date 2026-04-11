//! Proof harnesses for transmute between values and single-field wrapper structs.
//! These test the transparent-wrapper transmute rules.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

struct Wrapper(u32);

fn transmute_u32_to_wrapper() {
    let x: u32 = 42;
    let w: Wrapper = unsafe { transmute::<u32, Wrapper>(x) };
    assert!(w.0 == 42);
}

fn transmute_wrapper_to_u32() {
    let w = Wrapper(99);
    let x: u32 = unsafe { transmute::<Wrapper, u32>(w) };
    assert!(x == 99);
}

fn transmute_wrapper_roundtrip() {
    let x: u32 = 12345;
    let w: Wrapper = unsafe { transmute::<u32, Wrapper>(x) };
    let y: u32 = unsafe { transmute::<Wrapper, u32>(w) };
    assert!(x == y);
}

struct WrapperI64(i64);

fn transmute_i64_wrapper_roundtrip() {
    let x: i64 = -999;
    let w: WrapperI64 = unsafe { transmute::<i64, WrapperI64>(x) };
    let y: i64 = unsafe { transmute::<WrapperI64, i64>(w) };
    assert!(x == y);
}

struct WrapperU8(u8);

fn transmute_u8_wrapper() {
    let x: u8 = 255;
    let w: WrapperU8 = unsafe { transmute::<u8, WrapperU8>(x) };
    assert!(w.0 == 255);
    let y: u8 = unsafe { transmute::<WrapperU8, u8>(w) };
    assert!(y == 255);
}

fn main() {
    transmute_u32_to_wrapper();
    transmute_wrapper_to_u32();
    transmute_wrapper_roundtrip();
    transmute_i64_wrapper_roundtrip();
    transmute_u8_wrapper();
}
