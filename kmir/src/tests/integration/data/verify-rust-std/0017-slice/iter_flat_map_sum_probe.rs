fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let sum = slice
        .iter()
        .flat_map(|x| core::iter::once(*x))
        .sum::<i32>();

    assert!(sum == 6_i32);
}
