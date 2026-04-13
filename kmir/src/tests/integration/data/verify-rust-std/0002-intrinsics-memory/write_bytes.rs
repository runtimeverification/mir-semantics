fn main() {
    let mut buffer = [7u8, 8u8, 9u8, 10u8];

    unsafe {
        core::ptr::write_bytes(buffer.as_mut_ptr(), 0u8, buffer.len());
    }

    assert!(buffer[0] == 0);
    assert!(buffer[1] == 0);
    assert!(buffer[2] == 0);
    assert!(buffer[3] == 0);
}
