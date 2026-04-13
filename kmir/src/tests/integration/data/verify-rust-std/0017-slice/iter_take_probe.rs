fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let count = slice.iter().take(3_usize).count();

    assert!(count == 3_usize);
}
