fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    assert!(slice.ends_with(&[2_i32, 3_i32]));
    assert!(!slice.ends_with(&[1_i32, 2_i32]));
}
