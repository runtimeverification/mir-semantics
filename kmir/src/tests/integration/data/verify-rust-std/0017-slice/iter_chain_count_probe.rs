fn main() {
    let first = [1_i32];
    let second = [2_i32, 3_i32];
    let third = [4_i32, 5_i32, 6_i32];
    let count = first
        .iter()
        .chain(second.iter())
        .chain(third.iter())
        .count();

    assert!(count == 6_usize);
}
