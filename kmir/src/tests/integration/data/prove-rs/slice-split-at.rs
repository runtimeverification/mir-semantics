fn main() {
    let arr: [u8; 2] = [42, 255];
    let slice = arr.as_slice();
    let (left, right) = slice.split_at(1);
    assert!(left == [42]);
    assert!(right == [255]);
}