fn main() {
    let data = [7i32, 8i32, 9i32];
    let slice = core::ptr::slice_from_raw_parts(data.as_ptr(), 3);

    unsafe {
        assert!((*slice).len() == 3);
    }
}
