fn main() {
    let mut value: i32 = 5555;
    let value_ptr = core::ptr::addr_of_mut!(value);

    let copied: i32;
    unsafe {
        core::ptr::write(value_ptr, 7777);
        copied = core::ptr::read(value_ptr);
    }

    assert!(copied == 7777);
    assert!(value == 7777);
}
