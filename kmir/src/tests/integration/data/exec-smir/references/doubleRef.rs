fn main() {
    // double references
    let x = 42i8;
    let y = &x;
    let z = &y;

    assert!(**z == x); // uses CopyForDeref(*z)

    assert!(z == &&x); // compare instance &&i8, uses &&&i8 arguments
}
