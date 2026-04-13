fn main() {
    let source = [4_i32, 5_i32, 6_i32];
    let mut target = [0_i32, 0_i32, 0_i32];
    let source_slice = &source[..];
    let target_slice = &mut target[..];

    target_slice.copy_from_slice(source_slice);

    assert!(target_slice[0] == 4_i32);
    assert!(target_slice[1] == 5_i32);
    assert!(target_slice[2] == 6_i32);
}
