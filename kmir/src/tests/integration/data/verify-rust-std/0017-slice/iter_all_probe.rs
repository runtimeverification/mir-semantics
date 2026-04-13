fn main() {
    let slice = [2_i32, 4_i32, 6_i32];
    let all_even = slice.iter().all(|x| *x % 2_i32 == 0_i32);

    assert!(all_even);
}
