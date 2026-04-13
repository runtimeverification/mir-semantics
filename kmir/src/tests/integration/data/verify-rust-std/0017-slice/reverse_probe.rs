fn main() {
    let mut array = [1_i32, 2_i32, 3_i32, 4_i32];
    let slice = &mut array[..];

    slice.reverse();

    assert!(slice[0] == 4_i32);
    assert!(slice[1] == 3_i32);
    assert!(slice[2] == 2_i32);
    assert!(slice[3] == 1_i32);
}
