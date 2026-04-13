fn main() {
    let value = unsafe { core::mem::zeroed::<u32>() };

    assert!(value == 0);
}
