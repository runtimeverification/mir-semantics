fn main() {
    let data = [11i32, 22i32, 33i32];
    let ptr = data.as_ptr();
    let slice = unsafe { core::slice::from_raw_parts(ptr, 3) };

    assert!(slice.len() == 3);
    assert!(slice[0] == 11);
}
