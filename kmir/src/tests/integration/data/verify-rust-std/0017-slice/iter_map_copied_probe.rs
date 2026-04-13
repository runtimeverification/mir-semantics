fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let sum = slice.iter().copied().map(|x| x + 10_i32).sum::<i32>();

    assert!(sum == 36_i32);
}
