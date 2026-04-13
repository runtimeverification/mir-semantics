fn main() {
    let slice = [5_i32, 10_i32, 15_i32];
    let sum = slice.iter().inspect(|_| {}).copied().sum::<i32>();

    assert!(sum == 30_i32);
}
