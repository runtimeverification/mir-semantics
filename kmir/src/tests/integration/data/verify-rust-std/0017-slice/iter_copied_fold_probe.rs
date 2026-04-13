fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let product = slice.iter().copied().fold(1_i32, |a, b| a * b);

    assert!(product == 120_i32);
}
