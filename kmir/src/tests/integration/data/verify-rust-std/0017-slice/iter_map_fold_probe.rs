fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let sum = slice.iter().map(|x| *x * 2_i32).fold(0_i32, |a, b| a + b);

    assert!(sum == 12_i32);
}
