fn main() {
    let slice = [10_i32, 20_i32, 30_i32, 40_i32];
    let nth = slice.iter().nth(2_usize).unwrap();

    assert!(nth == &30_i32);
}
