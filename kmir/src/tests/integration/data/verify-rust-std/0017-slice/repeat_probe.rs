fn main() {
    let array = [1_i32, 2_i32];
    let repeated = array.repeat(2_usize);

    assert!(repeated.len() == 4_usize);
    assert!(repeated[0] == 1_i32);
    assert!(repeated[1] == 2_i32);
    assert!(repeated[2] == 1_i32);
    assert!(repeated[3] == 2_i32);
}
