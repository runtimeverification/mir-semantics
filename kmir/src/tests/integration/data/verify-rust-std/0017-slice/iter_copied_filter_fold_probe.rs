fn main() {
    let slice = [2_i32, 4_i32, 6_i32, 8_i32];
    let sum = slice
        .iter()
        .copied()
        .filter(|x| *x > 4_i32)
        .fold(0_i32, |a, b| a + b);

    assert!(sum == 14_i32);
}
