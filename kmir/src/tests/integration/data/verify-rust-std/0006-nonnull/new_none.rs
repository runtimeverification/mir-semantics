use std::ptr::NonNull;

fn main() {
    let raw = std::ptr::null_mut::<i32>();

    let result = NonNull::new(raw);

    assert!(result.is_none());
}
