fn main() {
    let nested = [[1_i32, 2_i32, 3_i32], [4_i32, 5_i32, 6_i32]];
    let count = nested.iter().flatten().count();

    assert!(count == 6_usize);
}
