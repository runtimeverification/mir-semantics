//! Proof harnesses for `core::intrinsics::transmute_unchecked` on integer types.
//! Tests the unchecked variant of transmute with integer roundtrips.

#![feature(core_intrinsics)]
#![allow(deprecated)]

use std::intrinsics::transmute_unchecked;

fn unchecked_u32_to_i32_roundtrip() {
    let x: u32 = 42;
    let y: i32 = unsafe { transmute_unchecked::<u32, i32>(x) };
    let z: u32 = unsafe { transmute_unchecked::<i32, u32>(y) };
    assert!(x == z);
}

fn unchecked_u64_to_i64_roundtrip() {
    let x: u64 = 0xDEAD_BEEF_CAFE_BABE;
    let y: i64 = unsafe { transmute_unchecked::<u64, i64>(x) };
    let z: u64 = unsafe { transmute_unchecked::<i64, u64>(y) };
    assert!(x == z);
}

fn unchecked_u8_to_i8() {
    let x: u8 = 200;
    let y: i8 = unsafe { transmute_unchecked::<u8, i8>(x) };
    let z: u8 = unsafe { transmute_unchecked::<i8, u8>(y) };
    assert!(x == z);
}

fn unchecked_u16_to_i16() {
    let x: u16 = 50000;
    let y: i16 = unsafe { transmute_unchecked::<u16, i16>(x) };
    let z: u16 = unsafe { transmute_unchecked::<i16, u16>(y) };
    assert!(x == z);
}

fn main() {
    unchecked_u32_to_i32_roundtrip();
    unchecked_u64_to_i64_roundtrip();
    unchecked_u8_to_i8();
    unchecked_u16_to_i16();
}
