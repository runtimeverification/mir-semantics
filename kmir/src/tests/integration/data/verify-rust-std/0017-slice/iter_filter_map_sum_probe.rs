fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let sum = slice
        .iter()
        .filter_map(|x| if *x > 3_i32 { Some(*x) } else { None })
        .sum::<i32>();

    assert!(sum == 9_i32);
}
