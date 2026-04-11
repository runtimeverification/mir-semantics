//! Comprehensive transmute roundtrip harnesses covering all integer widths.
//! Each function exercises transmute in both directions to verify roundtrip.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

fn roundtrip_u8_bytes() {
    let x: u8 = 0xAB;
    let bytes: [u8; 1] = unsafe { transmute::<u8, [u8; 1]>(x) };
    let y: u8 = unsafe { transmute::<[u8; 1], u8>(bytes) };
    assert!(x == y);
}

fn roundtrip_i16_bytes() {
    let x: i16 = -1234;
    let bytes: [u8; 2] = unsafe { transmute::<i16, [u8; 2]>(x) };
    let y: i16 = unsafe { transmute::<[u8; 2], i16>(bytes) };
    assert!(x == y);
}

fn roundtrip_u32_bytes() {
    let x: u32 = 0xDEADBEEF;
    let bytes: [u8; 4] = unsafe { transmute::<u32, [u8; 4]>(x) };
    let y: u32 = unsafe { transmute::<[u8; 4], u32>(bytes) };
    assert!(x == y);
}

fn roundtrip_i64_bytes() {
    let x: i64 = i64::MIN;
    let bytes: [u8; 8] = unsafe { transmute::<i64, [u8; 8]>(x) };
    let y: i64 = unsafe { transmute::<[u8; 8], i64>(bytes) };
    assert!(x == y);
}

fn roundtrip_u128_i128() {
    let x: u128 = u128::MAX;
    let y: i128 = unsafe { transmute::<u128, i128>(x) };
    let z: u128 = unsafe { transmute::<i128, u128>(y) };
    assert!(x == z);
    assert!(y == -1);
}

fn roundtrip_usize_isize() {
    let x: usize = usize::MAX;
    let y: isize = unsafe { transmute::<usize, isize>(x) };
    let z: usize = unsafe { transmute::<isize, usize>(y) };
    assert!(x == z);
}

fn main() {
    roundtrip_u8_bytes();
    roundtrip_i16_bytes();
    roundtrip_u32_bytes();
    roundtrip_i64_bytes();
    roundtrip_u128_i128();
    roundtrip_usize_isize();
}
