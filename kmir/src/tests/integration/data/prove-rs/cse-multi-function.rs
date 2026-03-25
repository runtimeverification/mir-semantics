fn pick_first(a: bool, _b: bool) -> bool {
    a
}

fn both_true(x: bool, y: bool) -> bool {
    if pick_first(x, y) {
        y
    } else {
        false
    }
}

fn main() {
    let r = both_true(true, true);
    assert!(r);
}
