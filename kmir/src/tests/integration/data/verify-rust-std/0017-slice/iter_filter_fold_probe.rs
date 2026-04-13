fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let sum = slice
        .iter()
        .filter(|x| **x % 2_i32 == 0_i32)
        .fold(0_i32, |a, b| a + b);

    assert!(sum == 6_i32);
}
