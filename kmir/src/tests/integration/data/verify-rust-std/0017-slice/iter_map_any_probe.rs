fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let has_twenty = slice.iter().map(|x| *x * 10_i32).any(|x| x == 20_i32);

    assert!(has_twenty);
}
