fn main() {
    let slice = [10_i32, 20_i32, 30_i32];
    let sum = slice
        .iter()
        .copied()
        .enumerate()
        .fold(0_i32, |a, (_, v)| a + v);

    assert!(sum == 60_i32);
}
