fn add1(x: i32) -> i32 {
    x + 1
}

fn main() {
    let x = 0;
    let y = add1(x);
    assert!(y == 1);
}