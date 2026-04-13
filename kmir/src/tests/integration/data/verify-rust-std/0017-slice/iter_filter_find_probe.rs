fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let found = slice.iter().filter(|x| **x > 3_i32).find(|x| **x == 5_i32);

    assert!(found.unwrap() == &5_i32);
}
