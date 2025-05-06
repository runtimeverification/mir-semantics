fn main() {
    let mut x = 5;
    let p1 = &mut x as *mut i32;
    let p2 = &mut x as *mut i32;
    unsafe {
        *p1 = 10;
        assert!(x == 10);
        *p2 = 20;
        assert!(x == 20);
    }
}
