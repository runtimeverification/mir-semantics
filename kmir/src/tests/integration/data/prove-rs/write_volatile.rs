fn main() {
    let mut a: i32 = 5555;
    let a_ptr = &mut a as *mut _;

    unsafe {
        std::ptr::write_volatile(a_ptr, 7777);
    }

    assert!(a == 7777);
}
