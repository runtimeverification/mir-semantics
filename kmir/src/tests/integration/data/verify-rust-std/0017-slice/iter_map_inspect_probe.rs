fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let sum = slice
        .iter()
        .map(|x| *x * 3_i32)
        .inspect(|_| {})
        .sum::<i32>();

    assert!(sum == 18_i32);
}
