fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let sum = slice
        .iter()
        .copied()
        .take_while(|x| *x <= 3_i32)
        .sum::<i32>();

    assert!(sum == 6_i32);
}
