fn main() {
    test_ptr_sub_basic();
    test_ptr_sub_to_start();
    test_ptr_add_then_sub();
}

// Test basic ptr::sub operation
fn test_ptr_sub_basic() {
    let arr = [1u8, 2, 3, 4, 5];
    let ptr = &arr[3] as *const u8; // Start at element 3 (value 4)

    unsafe {
        let p_back = ptr.sub(1);
        assert_eq!(*p_back, 3);

        let p_back2 = ptr.sub(2);
        assert_eq!(*p_back2, 2);
    }
}

// Test subtracting to reach the start
fn test_ptr_sub_to_start() {
    let arr = [10i32, 20, 30, 40, 50];
    let ptr = &arr[4] as *const i32; // Start at last element (value 50)

    unsafe {
        let p_start = ptr.sub(4);
        assert_eq!(*p_start, 10);
    }
}

// Test combination of add and sub
fn test_ptr_add_then_sub() {
    let arr = [100u32, 200, 300, 400, 500];
    let ptr = &arr[0] as *const u32;

    unsafe {
        let p_forward = ptr.add(3); // Move to element 3 (value 400)
        assert_eq!(*p_forward, 400);

        let p_back = p_forward.sub(1); // Move back to element 2 (value 300)
        assert_eq!(*p_back, 300);

        let p_back2 = p_back.sub(2); // Move back to element 0 (value 100)
        assert_eq!(*p_back2, 100);
    }
}
