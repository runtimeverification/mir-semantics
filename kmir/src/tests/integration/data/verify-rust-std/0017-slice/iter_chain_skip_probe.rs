fn main() {
    let left = [1_i32, 2_i32];
    let right = [3_i32, 4_i32, 5_i32];
    let sum = left
        .iter()
        .chain(right.iter())
        .skip(1_usize)
        .copied()
        .sum::<i32>();

    assert!(sum == 14_i32);
}
