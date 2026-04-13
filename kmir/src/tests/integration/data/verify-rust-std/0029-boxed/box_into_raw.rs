#[no_mangle]
pub fn verify_box_into_raw() {
    let ptr = Box::into_raw(Box::new(42i32));

    unsafe {
        assert_eq!(*ptr, 42);
        drop(Box::from_raw(ptr));
    }
}

fn main() {}
