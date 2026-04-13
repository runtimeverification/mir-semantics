use std::ops::Deref;

#[no_mangle]
pub fn verify_box_deref() {
    let boxed = Box::new(42i32);
    let dereferenced = boxed.deref();

    assert_eq!(*dereferenced, 42);
}

fn main() {}
