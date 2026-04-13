use std::ptr::NonNull;

const INPUT: i32 = 7;

fn main() {
    let mut value = INPUT;
    let raw = &mut value as *mut i32;

    let result = NonNull::new(raw);

    assert!(result.is_some());

    let nonnull = result.unwrap();
    let roundtrip = nonnull.as_ptr();
    assert!(roundtrip == raw);

    unsafe {
        assert!(*roundtrip == INPUT);
    }
}
