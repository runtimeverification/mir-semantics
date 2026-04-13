fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let has_nine = slice
        .iter()
        .map(|x| *x * 3_i32)
        .filter(|x| *x > 5_i32)
        .any(|x| x == 9_i32);

    assert!(has_nine);
}
