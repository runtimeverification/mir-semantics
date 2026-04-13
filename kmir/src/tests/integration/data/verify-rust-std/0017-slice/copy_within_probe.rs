fn main() {
    let mut array = [1_i32, 2_i32, 3_i32, 4_i32, 5_i32];
    let slice = &mut array[..];

    slice.copy_within(0..2, 3);

    assert!(slice[0] == 1_i32);
    assert!(slice[1] == 2_i32);
    assert!(slice[2] == 3_i32);
    assert!(slice[3] == 1_i32);
    assert!(slice[4] == 2_i32);
}
