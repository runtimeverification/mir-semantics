fn main() {
    let slice = [3_i32, 1_i32, 4_i32];
    let min = slice.iter().min().unwrap();

    assert!(min == &1_i32);
}
