fn main() {
    let mut value = String::new();

    value.push_str("hello");
    value.push_str("!");

    assert!(value.len() == 6);
    assert!(value == "hello!");
}
