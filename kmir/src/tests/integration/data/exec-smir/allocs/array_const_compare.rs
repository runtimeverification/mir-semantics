const I8_ARRAY: [i8; 3] = [1, -2, 3];
const U16_ARRAY: [u16; 3] = [100, 200, 300];

fn main() {
    // the array will be allocated twice, even if the same constant is used
    assert_eq!(I8_ARRAY, I8_ARRAY);
    // this uses an inlined array constant instead of the global one
    assert!(compare_to_stored(U16_ARRAY));
    // println!("All assertions passed!");
}

fn compare_to_stored(array: [u16;3]) -> bool {
    U16_ARRAY == array
}