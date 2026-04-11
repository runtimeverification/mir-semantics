//! Proof harnesses for transmute between byte arrays and integers.
//! Covers the byte-array-to-integer and integer-to-byte-array transmute paths.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

fn u32_to_bytes() {
    let x: u32 = 0x04030201;
    let bytes: [u8; 4] = unsafe { transmute::<u32, [u8; 4]>(x) };
    assert!(bytes[0] == 0x01);
    assert!(bytes[1] == 0x02);
    assert!(bytes[2] == 0x03);
    assert!(bytes[3] == 0x04);
}

fn bytes_to_u32() {
    let bytes: [u8; 4] = [0x01, 0x02, 0x03, 0x04];
    let x: u32 = unsafe { transmute::<[u8; 4], u32>(bytes) };
    assert!(x == 0x04030201);
}

fn u16_to_bytes() {
    let x: u16 = 0x0201;
    let bytes: [u8; 2] = unsafe { transmute::<u16, [u8; 2]>(x) };
    assert!(bytes[0] == 0x01);
    assert!(bytes[1] == 0x02);
}

fn bytes_to_u16() {
    let bytes: [u8; 2] = [0xAB, 0xCD];
    let x: u16 = unsafe { transmute::<[u8; 2], u16>(bytes) };
    assert!(x == 0xCDAB);
}

fn u32_byte_roundtrip() {
    let x: u32 = 12345678;
    let bytes: [u8; 4] = unsafe { transmute::<u32, [u8; 4]>(x) };
    let y: u32 = unsafe { transmute::<[u8; 4], u32>(bytes) };
    assert!(x == y);
}

fn main() {
    u32_to_bytes();
    bytes_to_u32();
    u16_to_bytes();
    bytes_to_u16();
    u32_byte_roundtrip();
}
