fn apply<F: FnOnce(u8, u8) -> u8>(f: F, a: u8, b: u8) -> u8 {
    f(a, b)
}

fn main() {
    let result = apply(|x, y| x + y, 10, 32);
    assert_eq!(result, 42);
}
