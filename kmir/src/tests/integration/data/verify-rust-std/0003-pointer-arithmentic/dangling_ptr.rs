fn main() {
    let ptr = core::ptr::NonNull::<i32>::dangling();

    assert!(!ptr.as_ptr().is_null());
}
