fn main() {
    let left = [1_i32, 2_i32];
    let right = [3_i32, 4_i32];
    let sum = left
        .iter()
        .map(|x| *x * 10_i32)
        .chain(right.iter().copied())
        .sum::<i32>();

    assert!(sum == 37_i32);
}
