fn main() {
    let left = [1_i32, 2_i32];
    let right = [3_i32, 4_i32];
    let sum = left
        .iter()
        .chain(right.iter())
        .fold(0_i32, |a, b| a + *b);

    assert!(sum == 10_i32);
}
