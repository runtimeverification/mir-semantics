fn main() {
    let value = String::with_capacity(8);

    assert!(value.len() == 0);
    assert!(value.capacity() >= 8);
}
