fn main() {
    let x = core::hint::black_box(42);
    assert!(x == 42);
}
