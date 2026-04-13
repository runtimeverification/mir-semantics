fn main() {
    let mut value: i32 = 1234;
    let value_ptr = &mut value as *mut i32;

    unsafe {
        core::ptr::drop_in_place(value_ptr);
    }

    assert!(value == 1234);
}
