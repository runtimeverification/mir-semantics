const U16_ARRAY: [u16; 3] = [100, 200, 300];
const NESTED: [[u16;3];2] = [U16_ARRAY, U16_ARRAY];

fn main() {
    // the array will be allocated twice, even if the same constant is used
    assert_eq!(NESTED, [[100,200,300],[100,200,300]]);
    // this uses an inlined array constant instead of the global one
    assert!(compare_to_stored(U16_ARRAY));
    assert!(compare_to_stored(NESTED[0]));
    // println!("All assertions passed!");
}

fn compare_to_stored(array: [u16;3]) -> bool {
    NESTED[1] == array
}