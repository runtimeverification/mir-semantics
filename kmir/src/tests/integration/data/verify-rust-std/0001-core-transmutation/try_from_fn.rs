#![feature(array_try_from_fn)]

// Harness for `try_from_fn` (core::array)
//
// Verifies that the success path constructs the full output array.

fn build_value(i: usize) -> Option<u8> {
    Some((i as u8) + 1)
}

fn main() {
    let cb: fn(usize) -> Option<u8> = build_value;
    let array: Option<[u8; 4]> = std::array::try_from_fn(cb);

    match array {
        Some(values) => {
            assert!(values[0] == 1);
            assert!(values[1] == 2);
            assert!(values[3] == 4);
        }
        None => assert!(false),
    }
}
