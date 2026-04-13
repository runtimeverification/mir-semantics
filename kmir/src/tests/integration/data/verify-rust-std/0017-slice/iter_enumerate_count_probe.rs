fn main() {
    let slice = [10_i32, 20_i32, 30_i32, 40_i32];
    let count = slice.iter().enumerate().count();

    assert!(count == 4_usize);
}
