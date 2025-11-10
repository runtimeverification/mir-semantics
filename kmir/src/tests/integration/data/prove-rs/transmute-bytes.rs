#![allow(clippy::transmute_bytes_to_bytes)]
#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

fn bytes_to_u64(bytes: [u8; 8]) -> u64 {
    let value = unsafe { transmute::<[u8; 8], u64>(bytes) };
    // prevent round-trip-transmute rule from simplifying this
    let enlarged = value as u128;
    let original = enlarged as u64;
    let roundtrip = unsafe { transmute::<u64, [u8; 8]>(original) };
    assert_eq!(roundtrip, bytes);
    value
}

fn u64_to_bytes(value: u64) -> [u8; 8] {
    let mut bytes = unsafe { transmute::<u64, [u8; 8]>(value) };
    let first = bytes[0];
    bytes[0] = 255u8;
    bytes[0] = first;
    let roundtrip = unsafe { transmute::<[u8; 8], u64>(bytes) };
    assert_eq!(roundtrip, value);
    bytes
}

fn main() {
    let bytes = [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF];
    let int = bytes_to_u64(bytes);
    assert_eq!(int, 0xEFCD_AB89_6745_2301);

    let roundtrip = u64_to_bytes(int);
    assert_eq!(roundtrip, bytes);

    let value = 0x1020_3040_5060_7080_u64;
    let value_roundtrip = bytes_to_u64(u64_to_bytes(value));
    assert_eq!(value_roundtrip, value);
}
