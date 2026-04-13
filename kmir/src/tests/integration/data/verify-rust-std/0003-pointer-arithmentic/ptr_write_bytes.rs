fn main() {
    let mut bytes = [1u8, 2u8, 3u8, 4u8];
    let bytes_ptr = bytes.as_mut_ptr();

    unsafe {
        core::ptr::write_bytes(bytes_ptr, 0u8, bytes.len());
    }

    assert!(bytes == [0u8; 4]);
}
