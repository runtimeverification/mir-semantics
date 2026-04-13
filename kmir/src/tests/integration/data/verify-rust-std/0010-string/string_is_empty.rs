fn main() {
    let empty = String::new();
    let nonempty = String::from("x");

    assert!(empty.is_empty());
    assert!(!nonempty.is_empty());
}
