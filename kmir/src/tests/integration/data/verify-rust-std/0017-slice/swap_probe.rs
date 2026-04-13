fn main() {
    let mut array = [1_i32, 2_i32, 3_i32];
    let slice = &mut array[..];

    slice.swap(0, 2);

    assert!(slice[0] == 3_i32);
    assert!(slice[1] == 2_i32);
    assert!(slice[2] == 1_i32);
}
