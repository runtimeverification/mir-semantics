fn main() {
    let slice = [10_i32, 20_i32, 30_i32];
    let sum = slice
        .iter()
        .map(|x| *x + 1_i32)
        .enumerate()
        .fold(0_usize, |acc, (i, _)| acc + i);

    assert!(sum == 3_usize);
}
