fn main() {
    let value = 5u32.saturating_sub(10);

    assert!(value == 0);
}
