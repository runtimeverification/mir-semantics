fn main() {
    let a = 42;
    let mut b = &a;
    b = &b;
    
    assert!(*b == 42);
}