//! Proof harnesses for `core::mem::transmute` on integer types.
//! Covers transmute roundtrips between signed/unsigned integer pairs.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

fn transmute_u32_to_i32() {
    let x: u32 = 42;
    let y: i32 = unsafe { transmute::<u32, i32>(x) };
    let z: u32 = unsafe { transmute::<i32, u32>(y) };
    assert!(x == z);
}

fn transmute_u32_to_i32_zero() {
    let x: u32 = 0;
    let y: i32 = unsafe { transmute::<u32, i32>(x) };
    let z: u32 = unsafe { transmute::<i32, u32>(y) };
    assert!(x == z);
}

fn transmute_u32_to_i32_max() {
    let x: u32 = u32::MAX;
    let y: i32 = unsafe { transmute::<u32, i32>(x) };
    assert!(y == -1);
    let z: u32 = unsafe { transmute::<i32, u32>(y) };
    assert!(x == z);
}

fn transmute_u16_to_i16() {
    let x: u16 = 1000;
    let y: i16 = unsafe { transmute::<u16, i16>(x) };
    let z: u16 = unsafe { transmute::<i16, u16>(y) };
    assert!(x == z);
}

fn transmute_u64_to_i64() {
    let x: u64 = 0xDEAD_BEEF_CAFE_BABE;
    let y: i64 = unsafe { transmute::<u64, i64>(x) };
    let z: u64 = unsafe { transmute::<i64, u64>(y) };
    assert!(x == z);
}

fn transmute_u8_to_i8() {
    let x: u8 = 255;
    let y: i8 = unsafe { transmute::<u8, i8>(x) };
    assert!(y == -1);
    let z: u8 = unsafe { transmute::<i8, u8>(y) };
    assert!(x == z);
}

fn transmute_usize_to_isize() {
    let x: usize = 12345;
    let y: isize = unsafe { transmute::<usize, isize>(x) };
    let z: usize = unsafe { transmute::<isize, usize>(y) };
    assert!(x == z);
}

fn main() {
    transmute_u32_to_i32();
    transmute_u32_to_i32_zero();
    transmute_u32_to_i32_max();
    transmute_u16_to_i16();
    transmute_u64_to_i64();
    transmute_u8_to_i8();
    transmute_usize_to_isize();
}
