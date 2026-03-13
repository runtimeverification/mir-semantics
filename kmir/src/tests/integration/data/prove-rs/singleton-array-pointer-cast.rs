fn main() {
    let mut x: u8 = 1;
    unsafe {
        let p: *mut u8 = &mut x;
        let q: *mut [u8; 1] = p as *mut [u8; 1];
        std::ptr::write(q, [2]);
    }
    assert!(x == 2);
}
