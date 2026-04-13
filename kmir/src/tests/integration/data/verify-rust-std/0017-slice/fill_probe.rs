fn main() {
    let mut array = [0_i32; 4];

    array.fill(7_i32);

    assert!(array[0] == 7_i32);
    assert!(array[1] == 7_i32);
    assert!(array[2] == 7_i32);
    assert!(array[3] == 7_i32);
}
