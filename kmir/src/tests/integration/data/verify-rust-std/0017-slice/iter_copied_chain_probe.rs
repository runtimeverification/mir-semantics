fn main() {
    let left = [1_i32, 2_i32];
    let right = [3_i32, 4_i32];
    let sum = left
        .iter()
        .copied()
        .chain(right.iter().copied())
        .sum::<i32>();

    assert!(sum == 10_i32);
}
