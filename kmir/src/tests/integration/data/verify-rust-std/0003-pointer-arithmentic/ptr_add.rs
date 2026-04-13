fn main() {
    let data = [2u32, 4u32, 6u32, 8u32];
    let base = data.as_ptr();

    unsafe {
        let ptr = base.add(3);
        assert!(*ptr == 8);
        assert!(ptr == &data[3] as *const u32);
    }
}
