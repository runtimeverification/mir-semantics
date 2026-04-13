fn main() {
    let left = [1_i32, 2_i32];
    let right = [3_i32, 4_i32, 5_i32];
    let count = left
        .iter()
        .chain(right.iter())
        .filter(|x| **x > 2_i32)
        .count();

    assert!(count == 3_usize);
}
