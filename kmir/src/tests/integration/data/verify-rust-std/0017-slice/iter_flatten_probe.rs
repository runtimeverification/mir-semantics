fn main() {
    let nested = [[1_i32, 2_i32], [3_i32, 4_i32]];
    let sum = nested.iter().flatten().copied().sum::<i32>();

    assert!(sum == 10_i32);
}
