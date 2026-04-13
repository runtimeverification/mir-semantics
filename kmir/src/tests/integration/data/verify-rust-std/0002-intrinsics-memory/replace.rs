fn main() {
    let mut value = 10_i32;

    let old = core::mem::replace(&mut value, 20_i32);

    assert!(old == 10_i32);
    assert!(value == 20_i32);
}
