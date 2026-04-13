#[no_mangle]
pub fn verify_box_new() {
    let boxed = Box::new(42i32);

    assert_eq!(*boxed, 42);
}

fn main() {}
