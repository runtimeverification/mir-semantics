fn main() {
    let len = [1; 2].len();
    let len2 = [4; 3].len();
    assert!(len == 2);
    assert!(len2 == 3);
}