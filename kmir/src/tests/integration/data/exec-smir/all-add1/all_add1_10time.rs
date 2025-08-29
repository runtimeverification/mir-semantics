fn add1(x: i32) -> i32 {
    x + 1
}

fn main() {
    let mut x = 0;
    let mut i = 0;
    while i < 10 {
        x = add1(x);
        i = add1(i);
    }
    assert!(x == 10);
}