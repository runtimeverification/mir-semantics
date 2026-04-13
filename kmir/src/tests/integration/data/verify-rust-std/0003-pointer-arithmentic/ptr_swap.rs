fn main() {
    let mut a = 12i32;
    let mut b = 34i32;

    unsafe {
        core::ptr::swap(&mut a as *mut i32, &mut b as *mut i32);
    }

    assert!(a == 34);
    assert!(b == 12);
}
