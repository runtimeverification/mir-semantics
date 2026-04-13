fn main() {
    let mut x = 10_i32;
    let mut y = 20_i32;

    core::mem::swap(&mut x, &mut y);

    assert!(x == 20_i32);
    assert!(y == 10_i32);
}
