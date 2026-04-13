fn main() {
    let left = [1_i32, 2_i32];
    let right = [3_i32];
    let sum = left
        .iter()
        .chain(right.iter())
        .map(|x| *x + 100_i32)
        .sum::<i32>();

    assert!(sum == 306_i32);
}
