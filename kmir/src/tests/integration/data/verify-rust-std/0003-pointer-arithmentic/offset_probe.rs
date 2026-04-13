fn main() {
    let arr = [10_u8, 20_u8, 30_u8];
    let ptr = arr.as_ptr();

    unsafe {
        let offset_ptr = ptr.offset(1);
        assert!(*offset_ptr == 20_u8);
    }
}
