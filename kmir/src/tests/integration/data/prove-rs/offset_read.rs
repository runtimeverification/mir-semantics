fn main() {
    let arr = [11, 22, 33];
    let subslice = &arr[1..];
    assert!(subslice == [22, 33]);
}