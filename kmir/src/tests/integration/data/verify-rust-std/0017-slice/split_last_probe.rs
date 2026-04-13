fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let split = slice.split_last();

    assert!(split.is_some());

    let (last, rest) = split.unwrap();
    assert!(*last == 3_i32);
    assert!(rest.len() == 2_usize);
    assert!(rest[0] == 1_i32);
    assert!(rest[1] == 2_i32);
}
