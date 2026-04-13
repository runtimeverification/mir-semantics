fn main() {
    let value = 456i32;
    let ptr = &value as *const i32;

    let copied = unsafe { core::ptr::read(ptr) };

    assert!(copied == value);
}
