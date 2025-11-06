fn main() {
    let value = 0x0123_4567_89AB_CDEF_u64;

    let native_bytes = value.to_ne_bytes();
    assert_eq!(u64::from_ne_bytes(native_bytes), value);

    let little_bytes = value.to_le_bytes();
    assert_eq!(u64::from_le_bytes(little_bytes), value);

    let big_bytes = value.to_be_bytes();
    assert_eq!(u64::from_be_bytes(big_bytes), value);
}
