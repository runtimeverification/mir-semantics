fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let last = slice.iter().last().unwrap();

    assert!(last == &3_i32);
}
