fn main() {
    let mut arr = [11, 22, 33];
    let subslice = &mut arr[1..];
    subslice[0] = 44;
    assert!(arr == [11, 44, 33]);
}