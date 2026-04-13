fn main() {
    let mut iter = [1_i32, 2_i32, 3_i32].iter();
    assert!(*iter.next().unwrap() == 1_i32);
    assert!(*iter.next().unwrap() == 2_i32);
    assert!(*iter.next().unwrap() == 3_i32);
    assert!(iter.next().is_none());
}
