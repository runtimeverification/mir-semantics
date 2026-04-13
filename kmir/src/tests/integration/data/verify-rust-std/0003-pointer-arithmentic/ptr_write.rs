fn main() {
    let mut a: i32 = 5555;
    let a_ptr = &mut a as *mut _;

    unsafe {
        core::ptr::write(a_ptr, 7777);
    }

    assert!(a == 7777);
}
