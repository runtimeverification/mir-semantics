fn main() {
    let arr = [0, 1, 2];

    let mut i: u8 = 0;

    for elem in arr {
        assert!(elem == i);
        i += 1;
    }
}
