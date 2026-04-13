#![feature(ascii_char)]

// Harness for `AsciiChar::from_u8` (core::ascii_char)
//
// Verifies that `from_u8` correctly validates and converts u8 values,
// returning Some(AsciiChar) for valid ASCII values.

use std::ascii::Char as AsciiChar;

fn main() {
    // Valid ASCII
    let a = AsciiChar::from_u8(0x41);
    assert!(a.is_some());
    assert!(a.unwrap().to_u8() == 0x41);

    // Null
    let null = AsciiChar::from_u8(0x00);
    assert!(null.is_some());
    assert!(null.unwrap().to_u8() == 0x00);

    // Max ASCII
    let max = AsciiChar::from_u8(0x7F);
    assert!(max.is_some());
    assert!(max.unwrap().to_u8() == 0x7F);

    // Space
    let space = AsciiChar::from_u8(0x20);
    assert!(space.is_some());
    assert!(space.unwrap().to_u8() == 0x20);
}
