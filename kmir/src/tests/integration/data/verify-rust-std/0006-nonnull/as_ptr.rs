use std::ptr::NonNull;

const INPUT: u32 = 42;

fn main() {
    let mut value = INPUT;
    let expected = std::ptr::addr_of_mut!(value);

    let nonnull = NonNull::from(&mut value);
    let raw = nonnull.as_ptr();

    assert!(raw == expected);

    unsafe {
        assert!(*raw == INPUT);
    }
}
