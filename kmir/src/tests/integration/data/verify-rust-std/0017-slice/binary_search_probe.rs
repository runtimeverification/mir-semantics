fn main() {
    let slice = [1_i32, 3_i32, 5_i32, 7_i32];
    let result = slice.binary_search(&5_i32);

    assert!(result == Ok(2_usize));
}
