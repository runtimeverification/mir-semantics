fn main() {
    let data = [11usize, 22usize, 33usize];
    let base = data.as_ptr();

    unsafe {
        let ptr = base.wrapping_add(1);
        assert!(*ptr == 22);
        assert!(ptr == base.add(1));
    }
}
