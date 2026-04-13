fn main() {
    let mut byte = 7u8;
    let byte_ptr = &mut byte as *mut u8;

    let read_back: u8;
    unsafe {
        core::ptr::write(byte_ptr, 42u8);
        read_back = core::ptr::read(byte_ptr as *const u8);
    }

    assert!(read_back == 42u8);
    assert!(byte == 42u8);
}
