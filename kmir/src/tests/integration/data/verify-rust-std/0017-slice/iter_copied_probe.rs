fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let sum = slice.iter().copied().sum::<i32>();

    assert!(sum == 6_i32);
}
