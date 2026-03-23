fn main() {
    let a: i32 = 5555;
    let a_ptr = &a as *const _;

    let b: i32;
    unsafe {
        b = std::ptr::read_volatile(a_ptr);
    }

    assert!(b == 5555);
}
