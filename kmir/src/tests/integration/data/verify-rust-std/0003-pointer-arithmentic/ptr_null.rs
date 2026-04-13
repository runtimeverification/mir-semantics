fn main() {
    let ptr = core::ptr::null::<i32>();

    assert!(ptr.is_null());
}
