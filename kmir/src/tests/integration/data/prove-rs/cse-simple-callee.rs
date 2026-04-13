fn double(x: u32) -> u32 {
    x + x
}

fn main() {
    let a: u32 = 5;
    let b = double(a);
    assert!(b == 10);
}
