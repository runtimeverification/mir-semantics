fn main() {
    let mut buffer = [1u8, 2u8, 3u8, 4u8, 5u8];

    unsafe {
        let ptr = buffer.as_mut_ptr();
        core::ptr::copy(ptr, ptr.add(1), 4);
    }

    assert!(buffer[0] == 1);
    assert!(buffer[1] == 1);
    assert!(buffer[2] == 2);
    assert!(buffer[3] == 3);
    assert!(buffer[4] == 4);
}
