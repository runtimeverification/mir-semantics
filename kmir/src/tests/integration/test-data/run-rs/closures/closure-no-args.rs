fn main() {
    let sum = || -> u32 { 42 };

    assert!(sum() == 42);
}