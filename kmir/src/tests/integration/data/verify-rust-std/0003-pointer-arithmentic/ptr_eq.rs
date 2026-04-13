fn main() {
    let value = 123i32;
    let left = &value;
    let right = &value;

    assert!(std::ptr::eq(left, right));
}
