fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let split = slice.split_first();

    assert!(split.is_some());

    let (first, rest) = split.unwrap();
    assert!(*first == 1_i32);
    assert!(rest.len() == 2_usize);
    assert!(rest[0] == 2_i32);
    assert!(rest[1] == 3_i32);
}
