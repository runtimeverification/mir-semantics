#![feature(ascii_char)]

// Harness for `char::as_ascii` (core::char)
//
// Verifies that `as_ascii` correctly returns Some(AsciiChar) for ASCII chars.

fn main() {
    // ASCII character 'A'
    let a = 'A';
    let ascii_a = a.as_ascii();
    assert!(ascii_a.is_some());
    assert!(ascii_a.unwrap().to_u8() == 0x41);

    // Null character
    let null = '\0';
    let ascii_null = null.as_ascii();
    assert!(ascii_null.is_some());
    assert!(ascii_null.unwrap().to_u8() == 0x00);

    // Max ASCII
    let del = '\x7F';
    let ascii_del = del.as_ascii();
    assert!(ascii_del.is_some());
    assert!(ascii_del.unwrap().to_u8() == 0x7F);

    // Space
    let space = ' ';
    let ascii_space = space.as_ascii();
    assert!(ascii_space.is_some());
    assert!(ascii_space.unwrap().to_u8() == 0x20);
}
