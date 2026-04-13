// Harness for `char::encode_utf16_raw` (core::char)
//
// Verifies that encode_utf16_raw correctly encodes characters as UTF-16.

fn main() {
    let mut buf = [0u16; 2];

    // BMP character 'A' -> single code unit
    let n = 'A'.encode_utf16(&mut buf);
    assert!(n.len() == 1);
    assert!(n[0] == 0x0041);

    // BMP character null
    let n = '\0'.encode_utf16(&mut buf);
    assert!(n.len() == 1);
    assert!(n[0] == 0x0000);

    // Max BMP character
    let n = '\u{FFFD}'.encode_utf16(&mut buf);
    assert!(n.len() == 1);
    assert!(n[0] == 0xFFFD);
}
