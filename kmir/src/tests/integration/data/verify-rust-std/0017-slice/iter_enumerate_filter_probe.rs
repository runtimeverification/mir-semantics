fn main() {
    let slice = [10_i32, 20_i32, 30_i32, 40_i32];
    let count = slice.iter().enumerate().filter(|(i, _)| *i > 1).count();

    assert!(count == 2_usize);
}
