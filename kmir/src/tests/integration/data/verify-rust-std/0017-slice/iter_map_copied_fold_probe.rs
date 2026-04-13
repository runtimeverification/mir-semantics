fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let sum = slice
        .iter()
        .copied()
        .map(|x| x * x)
        .fold(0_i32, |a, b| a + b);

    assert!(sum == 14_i32);
}
