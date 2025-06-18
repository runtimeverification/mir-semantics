// example functions producing pointer coercion and PtrToPtr casts

fn main() {
    if test(42) != 42 {
        test_unpack_success(42);
    };
}

// from p-token::processor::unpack_amount, casting a pointer to a slice to an array pointer 
const fn unpack_amount(instruction_data: &[u8]) -> u64 {
    // expected u64 (8)
    assert!(instruction_data.len() >= 8);
    // SAFETY: The minimum size of the instruction data is 8 bytes.
    unsafe {
        u64::from_le_bytes( // the `from_le_bytes` introduces `transmute` (not supported yet)
            *(instruction_data.as_ptr() as *const [u8; 8])
        ) 
    }
}

fn test_unpack_success(value: u64) {
    let bytes: &[u8] = &value.to_le_bytes()[..]; // another `transmute``
    let result = unpack_amount(bytes);
    assert!(result == value);
}

// simple array program performing similar casts as the above
fn slice_to_array_data(data: &[u8]) -> [u8; 8] {
    assert!(data.len() >= 8);
    unsafe { *(data.as_ptr() as *const [u8;8]) }
}

fn test(i: u8) -> u8 {
    let array = [i; 42];
    let result = slice_to_array_data(&array);
    result[7]
}