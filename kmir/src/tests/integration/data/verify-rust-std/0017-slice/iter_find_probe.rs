fn main() {
    let slice = [10_i32, 20_i32, 30_i32];
    let found = slice.iter().find(|x| **x == 20_i32).unwrap();

    assert!(*found == 20_i32);
}
