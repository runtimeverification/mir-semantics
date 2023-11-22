fn main() {
    let a = Box::new(5);
    let b = Box::new(5);

    assert!(a == b);
    assert!(*a == *b);
    assert!(*a == 5);
    // assert!(a == 5); // Not possible to equate Box::(Type) with Type
}