#[no_mangle]
pub fn verify_box_default() {
    let boxed = Box::<i32>::default();

    assert_eq!(*boxed, 0);
}

fn main() {}
