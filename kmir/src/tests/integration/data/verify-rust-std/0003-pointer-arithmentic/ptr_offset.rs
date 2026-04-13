fn main() {
    let data = [5i32, 10i32, 15i32, 20i32];
    let base = data.as_ptr();

    unsafe {
        let ptr = base.offset(2);
        assert!(*ptr == 15);
        assert!(ptr == base.add(2));
    }
}
