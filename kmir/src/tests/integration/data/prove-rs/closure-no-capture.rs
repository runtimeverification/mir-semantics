fn apply<F: FnOnce(u8) -> u8>(f: F, v: u8) -> u8 {
    f(v)
}

fn main() {
    let _ = repro();
}

fn repro() -> u8 {
    let f = |x: u8| x + 1;
    apply(f, 41u8)
}
