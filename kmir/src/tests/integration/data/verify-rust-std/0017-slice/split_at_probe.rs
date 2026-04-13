fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let (left, right) = slice.split_at(1);
    assert!(left.len() == 1_usize);
    assert!(right.len() == 2_usize);
    assert!(left[0] == 1_i32);
    assert!(right[0] == 2_i32);
}
