fn main() {
    let left = [1_i32, 2_i32, 3_i32];
    let right = [4_i32, 5_i32, 6_i32];
    let mut iter = left.iter().zip(right.iter());

    let (first_left, first_right) = iter.next().unwrap();
    assert!(*first_left == 1_i32);
    assert!(*first_right == 4_i32);

    let (second_left, second_right) = iter.next().unwrap();
    assert!(*second_left == 2_i32);
    assert!(*second_right == 5_i32);

    let (third_left, third_right) = iter.next().unwrap();
    assert!(*third_left == 3_i32);
    assert!(*third_right == 6_i32);

    assert!(iter.next().is_none());
}
