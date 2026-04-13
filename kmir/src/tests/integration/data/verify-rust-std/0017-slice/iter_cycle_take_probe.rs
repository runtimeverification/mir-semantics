fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let count = slice.iter().cycle().take(7_usize).count();

    assert!(count == 7_usize);
}
