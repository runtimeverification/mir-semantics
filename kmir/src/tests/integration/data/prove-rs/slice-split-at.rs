fn main() {
    let arr: [u8; 2] = [42, 255];
    let slice = arr.as_slice();
    let (left, right) = slice.split_at(1);
    assert!(left == [42]);
    assert!(right == [255]);

    let arr: [u8; 3] = [42, 255, 66];
    let slice = arr.as_slice();
    let (left, right) = slice.split_at(1);
    assert!(left == [42]);
    assert!(right == [255, 66]);

    // // This case currently failing
    // let arr: [u8; 3] = [42, 255, 66];
    // let slice = arr.as_slice();
    // let (left, right) = slice.split_at(3);
    // assert!(left == [42, 255, 66]);
    // assert!(right == []);
}
