fn main() {
    let slice = [1_u8, 2_u8, 3_u8];
    let sum = slice.iter().copied().sum::<u8>();

    assert!(sum == 6_u8);
}
