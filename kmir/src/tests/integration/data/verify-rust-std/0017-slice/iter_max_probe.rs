fn main() {
    let slice = [3_i32, 1_i32, 4_i32, 1_i32, 5_i32];
    let max = slice.iter().max().unwrap();

    assert!(max == &5_i32);
}
