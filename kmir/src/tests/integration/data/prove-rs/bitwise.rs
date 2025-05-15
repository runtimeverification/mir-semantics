fn and(x: i32, y: i32) -> i32 {
    x & y
}

fn or(x: i32, y: i32) -> i32 {
    x | y
}

fn xor(x: i32, y: i32) -> i32 {
    x ^ y
}

fn shift_left(x: i32, y: i32) -> i32 {
    x << y
}

fn shift_right(x: i32, y: i32) -> i32 {
    x >> y
}

fn main() {
    assert!(and(3, 4) == 0);

    assert!(or(3, 4) == 7);

    assert!(xor(3, 7) == 4);

    assert!(shift_left(1, 4) == 16);

    assert!(shift_right(32, 4) == 2);
}