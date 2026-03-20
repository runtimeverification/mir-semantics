fn apply<F: FnOnce(u8) -> u8>(f: F, v: u8) -> u8 {
    f(v)
}

fn main() {
    let delta: u8 = 1u8;
    let _captured = |x: u8| x + delta;

    let f = |x: u8| x + 1u8;
    assert_eq!(apply(f, 41u8), 42u8);
}
