fn main() {
    let min_value = core::cmp::min(3_i32, 5_i32);
    let max_value = core::cmp::max(3_i32, 5_i32);

    assert!(min_value == 3_i32);
    assert!(max_value == 5_i32);
}
