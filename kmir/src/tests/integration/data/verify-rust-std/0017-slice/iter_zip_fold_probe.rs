fn main() {
    let left = [1_i32, 2_i32, 3_i32];
    let right = [4_i32, 5_i32, 6_i32];
    let sum = left
        .iter()
        .zip(right.iter())
        .fold(0_i32, |acc, (a, b)| acc + *a + *b);

    assert!(sum == 21_i32);
}
