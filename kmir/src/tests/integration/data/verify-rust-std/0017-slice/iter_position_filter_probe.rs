fn main() {
    let slice = [5_i32, 10_i32, 15_i32, 20_i32];
    let count = slice.iter().filter(|x| **x > 8_i32).count();

    assert!(count == 3_usize);
}
