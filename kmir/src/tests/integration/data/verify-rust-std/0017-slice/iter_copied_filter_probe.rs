fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32];
    let sum = slice.iter().copied().filter(|x| *x > 2_i32).sum::<i32>();

    assert!(sum == 7_i32);
}
