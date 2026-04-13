// Harness for `char::from_u32` / `char_try_from_u32` (core::char::convert)
//
// Verifies that `char::from_u32` correctly validates and converts u32 values.

fn main() {
    // Valid ASCII character
    let c1 = char::from_u32(0x41);
    assert!(c1.is_some());
    assert!(c1.unwrap() == 'A');

    // Valid null character
    let c2 = char::from_u32(0x00);
    assert!(c2.is_some());
    assert!(c2.unwrap() == '\0');

    // Valid Unicode scalar value
    let c3 = char::from_u32(0x03B1);
    assert!(c3.is_some());
    assert!(c3.unwrap() as u32 == 0x03B1);

    // Valid maximum Unicode scalar value
    let c4 = char::from_u32(0x10FFFF);
    assert!(c4.is_some());
    assert!(c4.unwrap() as u32 == 0x10FFFF);
}
