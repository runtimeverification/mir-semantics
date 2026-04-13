fn main() {
    let slice = [10_i32, 20_i32, 30_i32];
    let position = slice.iter().position(|x| *x == 20_i32);

    assert!(position == Some(1_usize));
}
