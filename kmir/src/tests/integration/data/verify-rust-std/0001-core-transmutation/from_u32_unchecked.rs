/// Harness for `char::from_u32_unchecked` (core::char::convert)
///
/// Verifies that `from_u32_unchecked` correctly transmutes a valid u32
/// into its corresponding char value.

fn main() {
    // Basic ASCII characters
    let c1 = unsafe { char::from_u32_unchecked(0x41) }; // 'A'
    assert!(c1 == 'A');

    let c2 = unsafe { char::from_u32_unchecked(0x30) }; // '0'
    assert!(c2 == '0');

    // Null character
    let c3 = unsafe { char::from_u32_unchecked(0x00) };
    assert!(c3 == '\0');

    // Max ASCII
    let c4 = unsafe { char::from_u32_unchecked(0x7F) };
    assert!(c4 as u32 == 0x7F);

    // Unicode scalar value in BMP
    let c5 = unsafe { char::from_u32_unchecked(0x03B1) }; // Greek alpha
    assert!(c5 as u32 == 0x03B1);

    // Unicode scalar value outside BMP
    let c6 = unsafe { char::from_u32_unchecked(0x1F600) }; // Emoji
    assert!(c6 as u32 == 0x1F600);

    // Maximum valid Unicode scalar value
    let c7 = unsafe { char::from_u32_unchecked(0x10FFFF) };
    assert!(c7 as u32 == 0x10FFFF);
}
