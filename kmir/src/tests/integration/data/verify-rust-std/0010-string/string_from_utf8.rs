fn main() {
    let bytes = vec![104_u8, 105_u8];
    let value = String::from_utf8(bytes).unwrap();

    assert!(value == "hi");
}
