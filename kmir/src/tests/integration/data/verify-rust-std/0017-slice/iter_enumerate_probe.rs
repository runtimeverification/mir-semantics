fn main() {
    let slice = [10_i32, 20_i32, 30_i32];
    let mut iter = slice.iter().enumerate();

    let (first_index, first_value) = iter.next().unwrap();
    assert!(first_index == 0_usize);
    assert!(*first_value == 10_i32);

    let (second_index, second_value) = iter.next().unwrap();
    assert!(second_index == 1_usize);
    assert!(*second_value == 20_i32);

    let (third_index, third_value) = iter.next().unwrap();
    assert!(third_index == 2_usize);
    assert!(*third_value == 30_i32);

    assert!(iter.next().is_none());
}
