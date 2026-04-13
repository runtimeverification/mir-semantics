fn main() {
    let slice = [1_u8, 2_u8, 3_u8];
    let ptr = slice.as_ptr();

    let first = unsafe { *ptr };
    assert!(first == 1_u8);
}
