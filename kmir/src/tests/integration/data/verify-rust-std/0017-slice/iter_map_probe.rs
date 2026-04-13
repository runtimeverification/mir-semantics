fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let mut seen = 0_usize;

    slice.iter().map(|x| *x * 2_i32).for_each(|value| {
        if seen == 0_usize {
            assert!(value == 2_i32);
        } else if seen == 1_usize {
            assert!(value == 4_i32);
        } else if seen == 2_usize {
            assert!(value == 6_i32);
        } else {
            assert!(false);
        }
        seen += 1_usize;
    });

    assert!(seen == 3_usize);
}
