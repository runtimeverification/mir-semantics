struct Pair {
    head: i64,
    tail: i8,
}

fn read_via_cast(pair: &Pair) -> i64 {
    unsafe { *(pair as *const Pair as *const i64) }
}

fn main() {
    let pair = Pair { head: 7, tail: 1 };
    assert!(read_via_cast(&pair) == 7);
}
