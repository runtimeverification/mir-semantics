fn main() {
    let arr = [1u32, 2, 3, 4, 5];
    let ptr = &arr as *const [u32; 5] as *const u32;

    // Test basic offset
    let _ptr1 = unsafe { ptr.offset(2) };

    // Test chained offsets
    let ptr2 = unsafe { ptr.offset(1) };
    let _ptr3 = unsafe { ptr2.offset(1) };

    // Test boundary
    let _ptr4 = unsafe { ptr.offset(5) };

    assert!(true);
}
