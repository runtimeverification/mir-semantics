fn main() {
    let mut value: i32 = 5555;
    let value_ptr = &mut value as *mut _;

    let old_value: i32;
    unsafe {
        old_value = core::ptr::read(value_ptr);
        core::ptr::write(value_ptr, 7777);
    }

    assert!(old_value == 5555);
    assert!(value == 7777);
}
