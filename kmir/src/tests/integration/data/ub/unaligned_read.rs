fn main() {
    let mut x: [u8; 4] = [0; 4];
    unsafe {
        let p = x.as_mut_ptr().add(1) as *mut u32;
        *p = 0xDEADBEEF;
    }
}
