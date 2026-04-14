fn add_to(x: &u32, y: u32) -> u32 {
    *x + y
}

fn main() {
    let a: u32 = 3;
    let b: u32 = 7;
    let result = add_to(&a, b);
    assert!(result == 10);
}
