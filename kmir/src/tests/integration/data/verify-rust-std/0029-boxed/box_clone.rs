#[no_mangle]
pub fn verify_box_clone() {
    let boxed = Box::new(42i32);
    let cloned = boxed.clone();

    assert_eq!(*boxed, 42);
    assert_eq!(*cloned, 42);
}

fn main() {}
