fn main() {
    let slice = [10_i32, 20_i32, 30_i32, 40_i32];
    let has_thirty = slice
        .iter()
        .copied()
        .filter(|x| *x >= 20_i32)
        .any(|x| x == 30_i32);

    assert!(has_thirty);
}
