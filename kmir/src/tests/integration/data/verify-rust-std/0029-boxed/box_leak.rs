#[no_mangle]
pub fn verify_box_leak() {
    let leaked = Box::leak(Box::new(42i32));

    assert_eq!(*leaked, 42);
}

fn main() {}
