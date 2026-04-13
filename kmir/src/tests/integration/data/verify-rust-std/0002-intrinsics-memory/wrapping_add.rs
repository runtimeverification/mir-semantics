fn main() {
    let value = u32::MAX.wrapping_add(1);

    assert!(value == 0);
}
