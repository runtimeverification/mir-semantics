fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32];
    let sum = slice
        .iter()
        .filter_map(|x| if *x > 2_i32 { Some(*x * 10_i32) } else { None })
        .fold(0_i32, |a, b| a + b);

    assert!(sum == 70_i32);
}
