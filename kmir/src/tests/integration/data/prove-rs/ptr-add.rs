fn main() {
    test_ptr_add_basic();
    test_ptr_add_multiple();
    test_ptr_add_to_end();
}

// Test basic ptr::add operation
fn test_ptr_add_basic() {
    let arr = [10u8, 20, 30, 40];
    let ptr = &arr[0] as *const u8;

    unsafe {
        let p1 = ptr.add(1);
        assert_eq!(*p1, 20);

        let p3 = ptr.add(3);
        assert_eq!(*p3, 40);
    }
}

// Test multiple add operations
fn test_ptr_add_multiple() {
    let arr = [5i32, 10, 15, 20, 25, 30];
    let ptr = &arr[0] as *const i32;

    unsafe {
        let p1 = ptr.add(1);
        assert_eq!(*p1, 10);

        let p2 = p1.add(1); // Cumulative offset: 2
        assert_eq!(*p2, 15);

        let p3 = p2.add(1); // Cumulative offset: 3
        assert_eq!(*p3, 20);
    }
}

// Test adding to reach the end
fn test_ptr_add_to_end() {
    let arr = [100u32, 200, 300];
    let ptr = &arr[0] as *const u32;

    unsafe {
        let p_end = ptr.add(2);
        assert_eq!(*p_end, 300);
    }
}
