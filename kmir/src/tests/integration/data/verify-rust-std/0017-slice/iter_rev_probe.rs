fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut iter = slice.iter().rev();
    let first = iter.next().unwrap();

    assert!(first == &3_i32);
}
