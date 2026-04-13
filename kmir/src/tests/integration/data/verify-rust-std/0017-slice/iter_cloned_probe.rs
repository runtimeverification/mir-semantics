fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let count = slice.iter().cloned().count();

    assert!(count == 3_usize);
}
