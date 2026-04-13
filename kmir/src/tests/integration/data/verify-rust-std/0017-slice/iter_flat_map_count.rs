fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let count = slice.iter().flat_map(|x| [*x, *x + 10_i32]).count();

    assert!(count == 6_usize);
}
