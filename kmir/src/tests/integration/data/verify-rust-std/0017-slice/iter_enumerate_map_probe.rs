fn main() {
    let slice = [10_i32, 20_i32, 30_i32];
    let sum = slice
        .iter()
        .enumerate()
        .map(|(i, v)| i as i32 + *v)
        .sum::<i32>();

    assert!(sum == 63_i32);
}
