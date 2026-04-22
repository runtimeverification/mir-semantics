fn read_nested_ref(x: &&u32) -> u32 {
    **x
}

#[no_mangle]
pub fn caller(x: u32) {
    let first = &x;
    let second = &first;
    let result = read_nested_ref(second);

    assert!(result == x);
}

fn main() {}
