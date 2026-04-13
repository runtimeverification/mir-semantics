fn main() {
    let data = [9u16, 18u16, 27u16, 36u16];

    unsafe {
        let end = data.as_ptr().add(3);
        let ptr = end.sub(2);

        assert!(*ptr == 18);
        assert!(ptr == &data[1] as *const u16);
    }
}
