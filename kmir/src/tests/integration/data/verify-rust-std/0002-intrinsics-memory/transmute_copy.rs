fn main() {
    let value = 0x1234_5678_u32;
    let bytes: [u8; 4] = unsafe { core::mem::transmute_copy(&value) };
    let roundtrip = u32::from_ne_bytes(bytes);

    assert!(roundtrip == value);
    assert!(value == 0x1234_5678_u32);
}
