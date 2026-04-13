fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut count = 0_usize;

    slice.iter().for_each(|_| {
        count += 1_usize;
    });

    assert!(count == 3_usize);
}
