fn main() {
    let value: i32 = 5555;
    let value_ptr = core::ptr::addr_of!(value);

    let copied: i32;
    unsafe {
        copied = core::ptr::read(value_ptr);
    }

    assert!(copied == 5555);
}
