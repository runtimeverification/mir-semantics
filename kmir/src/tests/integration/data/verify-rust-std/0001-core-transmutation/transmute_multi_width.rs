//! Proof harnesses for transmute between various same-width integer pairs.
//! Tests all standard integer width roundtrips.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

fn transmute_u128_to_i128_roundtrip() {
    let x: u128 = 0xDEAD_BEEF_CAFE_BABE_1234_5678_9ABC_DEF0;
    let y: i128 = unsafe { transmute::<u128, i128>(x) };
    let z: u128 = unsafe { transmute::<i128, u128>(y) };
    assert!(x == z);
}

fn transmute_i128_negative() {
    let x: i128 = -1;
    let y: u128 = unsafe { transmute::<i128, u128>(x) };
    let z: i128 = unsafe { transmute::<u128, i128>(y) };
    assert!(x == z);
}

fn transmute_u32_bytes_roundtrip() {
    let x: u32 = 0xDEADBEEF;
    let bytes: [u8; 4] = unsafe { transmute::<u32, [u8; 4]>(x) };
    let y: u32 = unsafe { transmute::<[u8; 4], u32>(bytes) };
    assert!(x == y);
}

fn transmute_i32_bytes_roundtrip() {
    let x: i32 = -12345;
    let bytes: [u8; 4] = unsafe { transmute::<i32, [u8; 4]>(x) };
    let y: i32 = unsafe { transmute::<[u8; 4], i32>(bytes) };
    assert!(x == y);
}

fn transmute_u16_bytes_roundtrip() {
    let x: u16 = 0xABCD;
    let bytes: [u8; 2] = unsafe { transmute::<u16, [u8; 2]>(x) };
    let y: u16 = unsafe { transmute::<[u8; 2], u16>(bytes) };
    assert!(x == y);
}

fn transmute_u64_bytes_full_roundtrip() {
    let x: u64 = 0x0102030405060708;
    let bytes: [u8; 8] = unsafe { transmute::<u64, [u8; 8]>(x) };
    // Check little-endian layout
    assert!(bytes[0] == 0x08);
    assert!(bytes[7] == 0x01);
    let y: u64 = unsafe { transmute::<[u8; 8], u64>(bytes) };
    assert!(x == y);
}

fn main() {
    transmute_u128_to_i128_roundtrip();
    transmute_i128_negative();
    transmute_u32_bytes_roundtrip();
    transmute_i32_bytes_roundtrip();
    transmute_u16_bytes_roundtrip();
    transmute_u64_bytes_full_roundtrip();
}
