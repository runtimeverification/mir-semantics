fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let count = slice.iter().map(|x| [*x, *x * 10_i32]).flatten().count();

    assert!(count == 6_usize);
}
