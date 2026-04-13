fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let last = slice
        .iter()
        .scan(0_i32, |acc, x| {
            *acc += x;
            Some(*acc)
        })
        .last()
        .unwrap();

    assert!(last == 6_i32);
}
