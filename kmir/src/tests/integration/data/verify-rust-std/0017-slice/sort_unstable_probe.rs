fn main() {
    let mut array = [3_i32, 1_i32, 2_i32];
    let slice = &mut array[..];

    slice.sort_unstable();

    assert!(slice[0] == 1_i32);
    assert!(slice[1] == 2_i32);
    assert!(slice[2] == 3_i32);
}
