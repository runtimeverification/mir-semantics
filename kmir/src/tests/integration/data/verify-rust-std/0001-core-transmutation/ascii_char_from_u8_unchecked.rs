#![feature(ascii_char)]

// Harness for `AsciiChar::from_u8_unchecked` (core::ascii_char)
//
// Verifies that `from_u8_unchecked` correctly creates AsciiChar values
// from valid ASCII byte values.

use std::ascii::Char as AsciiChar;

fn main() {
    // Valid ASCII: 'A' = 0x41
    let a = unsafe { AsciiChar::from_u8_unchecked(0x41) };
    assert!(a.to_u8() == 0x41);

    // Valid ASCII: '0' = 0x30
    let z = unsafe { AsciiChar::from_u8_unchecked(0x30) };
    assert!(z.to_u8() == 0x30);

    // Null byte
    let null = unsafe { AsciiChar::from_u8_unchecked(0x00) };
    assert!(null.to_u8() == 0x00);

    // Max ASCII value = 0x7F
    let max = unsafe { AsciiChar::from_u8_unchecked(0x7F) };
    assert!(max.to_u8() == 0x7F);

    // Space
    let space = unsafe { AsciiChar::from_u8_unchecked(0x20) };
    assert!(space.to_u8() == 0x20);
}
