fn main() {
    let a = 42;
    let b = &a;
    let c = &b;
    
    assert!(**c == 42);
}