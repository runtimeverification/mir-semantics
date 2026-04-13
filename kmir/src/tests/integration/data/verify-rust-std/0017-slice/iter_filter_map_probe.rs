fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32];
    let count = slice
        .iter()
        .filter_map(|x| if *x > 2_i32 { Some(*x * 10_i32) } else { None })
        .count();

    assert!(count == 2_usize);
}
