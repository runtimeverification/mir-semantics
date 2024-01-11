fn main() {
    let a = [1, 2, 3, 4];

    let b = &a[1..3];

    assert!(b == [2, 3]);
}