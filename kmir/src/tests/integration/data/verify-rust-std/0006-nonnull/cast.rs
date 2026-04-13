use std::ptr::NonNull;

const INPUT: u32 = 0x0102_0304;

fn main() {
    let mut value = INPUT;
    let base = std::ptr::addr_of_mut!(value);

    let nonnull_u32 = NonNull::from(&mut value);
    let nonnull_u8 = nonnull_u32.cast::<u8>();

    assert!(nonnull_u8.as_ptr() == base.cast::<u8>());

    let roundtrip = nonnull_u8.cast::<u32>();
    assert!(roundtrip.as_ptr() == base);

    unsafe {
        assert!(*roundtrip.as_ptr() == INPUT);
    }
}
