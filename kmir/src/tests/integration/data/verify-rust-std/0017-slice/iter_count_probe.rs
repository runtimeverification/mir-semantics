fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut count = 0_usize;
    for _elem in slice.iter() {
        count += 1_usize;
    }
    assert!(count == 3_usize);
}
