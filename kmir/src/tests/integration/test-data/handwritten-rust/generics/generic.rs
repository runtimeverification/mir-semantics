fn index_slice<T>(slice:&[T], index: usize) -> &T {
    &(slice[index])
}

fn main() {
    let numbers = [1, 2, 3, 4, 5];
    let letters = ['a', 'b', 'c', 'd', 'e'];

    let middle_number:&i32  = index_slice(&numbers[..], 2);
    let middle_letter:&char = index_slice(&letters[..], 2);

    assert!(*middle_number == 3);
    assert!(*middle_letter == 'c');
}