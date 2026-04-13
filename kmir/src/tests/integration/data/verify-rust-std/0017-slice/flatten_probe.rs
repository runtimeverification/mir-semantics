#![feature(slice_flatten)]

fn main() {
    let array = [[1_i32, 2_i32], [3_i32, 4_i32]];
    let flattened = array.as_flattened();

    assert!(flattened.len() == 4_usize);
    assert!(flattened[0] == 1_i32);
    assert!(flattened[1] == 2_i32);
    assert!(flattened[2] == 3_i32);
    assert!(flattened[3] == 4_i32);
}
