fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32, 6_i32];
    let sum = slice.iter().skip(1_usize).take(3_usize).copied().sum::<i32>();

    assert!(sum == 9_i32);
}
