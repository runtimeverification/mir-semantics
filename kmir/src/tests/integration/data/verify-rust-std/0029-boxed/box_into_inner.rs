#[no_mangle]
pub fn verify_box_into_inner() {
    let boxed = Box::new(42i32);
    let inner = *boxed;

    assert_eq!(inner, 42);
}

fn main() {}
