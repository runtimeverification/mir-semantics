fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut chunks = slice.chunks(2);

    let first = chunks.next().unwrap();
    assert!(first.len() == 2_usize);
    assert!(first[0] == 1_i32);
    assert!(first[1] == 2_i32);

    let second = chunks.next().unwrap();
    assert!(second.len() == 1_usize);
    assert!(second[0] == 3_i32);

    assert!(chunks.next().is_none());
}
