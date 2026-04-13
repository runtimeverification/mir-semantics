fn main() {
    let value: i32 = 0x11223344;
    let int_ptr = &value as *const i32;
    let byte_ptr = int_ptr as *const u8;

    assert!(!byte_ptr.is_null());
}
