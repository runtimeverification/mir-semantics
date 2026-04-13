fn main() {
    let slice = [1_i32, 2_i32, 3_i32];
    let total = slice
        .iter()
        .scan(0_i32, |acc, x| {
            *acc += *x;
            Some(*acc)
        })
        .sum::<i32>();

    assert!(total == 10_i32);
}
