fn main() {
    let slice = [1_i32, 2_i32, 3_i32, 4_i32];
    let sum = slice.iter().fold(0_i32, |acc, x| acc + *x);

    assert!(sum == 10_i32);
}
