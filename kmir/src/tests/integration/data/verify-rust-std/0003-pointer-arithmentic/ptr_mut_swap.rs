fn main() {
    let mut a = 12i32;
    let mut b = 34i32;
    let a_ptr = &mut a as *mut i32;
    let b_ptr = &mut b as *mut i32;

    unsafe {
        let tmp = core::ptr::read(a_ptr);
        let b_val = core::ptr::read(b_ptr);
        core::ptr::write(a_ptr, b_val);
        core::ptr::write(b_ptr, tmp);
    }

    assert!(a == 34);
    assert!(b == 12);
}
