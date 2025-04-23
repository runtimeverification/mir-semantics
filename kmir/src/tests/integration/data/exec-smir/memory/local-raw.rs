fn main() {
    let mut x: u32 = 3;
    let y: *mut u32 = &mut x;
    unsafe { *y = 0; }
}