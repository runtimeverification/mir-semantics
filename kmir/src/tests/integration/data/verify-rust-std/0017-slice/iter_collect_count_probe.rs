fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let count = slice.iter().copied().count();

    assert!(count == 5_usize);
}
