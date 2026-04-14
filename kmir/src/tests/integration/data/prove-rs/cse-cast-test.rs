fn as_usize(x: u32) -> usize {
    x as usize
}

fn main() {
    let a: u32 = 5;
    let b = as_usize(a);
    assert!(b == 5);
}
