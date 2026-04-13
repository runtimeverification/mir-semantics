fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let sum = slice.iter().copied().skip(2_usize).sum::<i32>();

    assert!(sum == 12_i32);
}
