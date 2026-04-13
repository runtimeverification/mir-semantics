fn main() {
    let mut value: i32 = 5555;
    let value_ptr = {
        let value_ref = &mut value;
        value_ref as *mut i32
    };

    unsafe {
        core::ptr::write(value_ptr, 7777);
    }

    assert!(value == 7777);
}
