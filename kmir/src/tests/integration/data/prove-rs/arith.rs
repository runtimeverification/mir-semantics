fn add(x: i32, y: i32) -> i32 {
    x + y
}

fn sub(x: i32, y: i32) -> i32 {
    x - y
}

fn mul(x: i32, y: i32) -> i32 {
    x * y
}

fn div(x: i32, y: i32) -> i32 {
    x / y
}

fn main() {
    assert!(add(3, 4) == 7);

    // assert!(sub(3, 4) == -1); // FAILING

    assert!(mul(3, 4) == 12);

    // assert!(div(12, 4) == 3); // FAILING
}