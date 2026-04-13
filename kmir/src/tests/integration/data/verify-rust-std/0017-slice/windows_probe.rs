fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut windows = slice.windows(2);

    let first = windows.next().unwrap();
    assert!(first[0] == 1_i32);
    assert!(first[1] == 2_i32);

    let second = windows.next().unwrap();
    assert!(second[0] == 2_i32);
    assert!(second[1] == 3_i32);

    assert!(windows.next().is_none());
}
