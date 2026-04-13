fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let count = slice.iter().map(|x| *x + 1_i32).count();

    assert!(count == 3_usize);
}
