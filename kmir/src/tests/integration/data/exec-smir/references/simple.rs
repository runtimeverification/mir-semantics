fn main() {
    let x = 42i8;
    let y = &x;
    let z = *y;

    assert!(z == x);
}
