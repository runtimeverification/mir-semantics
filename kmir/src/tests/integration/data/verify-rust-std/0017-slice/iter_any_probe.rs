fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let has_two = slice.iter().any(|x| *x == 2_i32);

    assert!(has_two);
}
