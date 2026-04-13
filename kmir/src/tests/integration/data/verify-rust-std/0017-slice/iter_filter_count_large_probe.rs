fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32, 6_i32, 7_i32, 8_i32, 9_i32, 10_i32];
    let count = slice.iter().filter(|x| **x > 5_i32).count();

    assert!(count == 5_usize);
}
