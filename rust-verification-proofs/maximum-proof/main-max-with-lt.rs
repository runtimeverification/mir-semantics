
fn main() {

    let a:isize = 42;
    let b:isize = -43;
    let c:isize = 0;

    let result = maximum(a, b, c);

    assert!(result >= a && result >= b && result >= c
        && (result == a || result == b || result == c ) );
}

fn maximum(a: isize, b: isize, c: isize) -> isize {
    // max(a, max(b, c))
    let max_ab = if a < b {b} else {a};
    if max_ab < c {c} else {max_ab}
}
