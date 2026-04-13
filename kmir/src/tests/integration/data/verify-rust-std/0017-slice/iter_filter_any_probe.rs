fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let has_five = slice.iter().filter(|x| **x > 3_i32).any(|x| *x == 5_i32);

    assert!(has_five);
}
