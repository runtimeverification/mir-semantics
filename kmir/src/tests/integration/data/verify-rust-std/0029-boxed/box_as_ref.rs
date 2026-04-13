#[no_mangle]
pub fn verify_box_as_ref() {
    let boxed = Box::new(42i32);
    let reference = &*boxed;

    assert_eq!(reference, &42);
}

fn main() {}
