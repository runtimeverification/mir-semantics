fn aliasing_refs_have_same_pointer() {
    let value = 42_i32;
    let first = &value;
    let second = &value;

    assert!((first as *const i32) == (second as *const i32));
    assert!(std::ptr::eq(first, second));
}

fn distinct_locals_have_distinct_pointers() {
    let left = 10_i32;
    let right = 10_i32;

    assert!((&left as *const i32) != (&right as *const i32));
}

fn array_element_addresses_are_distinct() {
    let items = [3_u8, 5, 7];
    let first = &items[0];
    let first_again = &items[0];
    let second = &items[1];

    assert!((first as *const u8) == (first_again as *const u8));
    assert!((first as *const u8) != (second as *const u8));
}

fn reborrow_mut_pointer_roundtrip() {
    let mut byte = 0_u8;
    let ptr = &mut byte as *mut u8;

    unsafe {
        *ptr = 1;
    }

    assert_eq!(byte, 1);
}

fn main() {
    aliasing_refs_have_same_pointer();
    distinct_locals_have_distinct_pointers();
    array_element_addresses_are_distinct();
    reborrow_mut_pointer_roundtrip();
}
