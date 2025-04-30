fn cmp_lt(x: i32, y: i32) -> bool {
    x < y
}

fn cmp_le(x: i32, y: i32) -> bool {
    x <= y
}

fn cmp_gt(x: i32, y: i32) -> bool {
    x > y
}

fn cmp_ge(x: i32, y: i32) -> bool {
    x >= y
}

fn cmp_eq(x: i32, y: i32) -> bool {
    x == y
}

fn cmp_neq(x: i32, y: i32) -> bool {
    x != y
}

fn main() {
    assert!( cmp_lt(3, 4));
    assert!(!cmp_lt(4, 3));
    assert!(!cmp_lt(4, 4));

    assert!( cmp_le(3, 4));
    assert!(!cmp_le(4, 3));
    assert!( cmp_le(4, 4));

    assert!(!cmp_gt(3, 4));
    assert!( cmp_gt(4, 3));
    assert!(!cmp_gt(4, 4));

    assert!(!cmp_ge(3, 4));
    assert!( cmp_ge(4, 3));
    assert!( cmp_ge(4, 4));

    assert!(!cmp_eq(4, 3));
    assert!( cmp_eq(4, 4));

    assert!( cmp_neq(4, 3));
    assert!(!cmp_neq(4, 4));
}