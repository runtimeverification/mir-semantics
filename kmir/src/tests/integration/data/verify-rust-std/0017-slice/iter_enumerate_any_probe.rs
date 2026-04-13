fn main() {
    let slice = [5_i32, 10_i32, 15_i32];
    let has_index_two = slice
        .iter()
        .enumerate()
        .any(|(i, _)| i == 2_usize);

    assert!(has_index_two);
}
