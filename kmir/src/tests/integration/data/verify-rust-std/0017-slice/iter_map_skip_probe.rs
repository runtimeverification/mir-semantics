fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let sum = slice.iter().map(|x| *x * 2_i32).skip(2_usize).sum::<i32>();

    assert!(sum == 24_i32);
}
