#![feature(core_intrinsics)]
use std::intrinsics::offset;

fn main() {
    test_offset_zero();
    test_offset_positive();
    test_offset_to_end();
    test_offset_negative();
}

// Test offset by 0 (trivial case)
fn test_offset_zero() {
    let arr = [1i32, 2, 3, 4, 5];
    let ptr = &arr[0] as *const i32;

    unsafe {
        let p0 = offset(ptr, 0isize);
        assert_eq!(*p0, 1);
    }
}

// Test positive offset
fn test_offset_positive() {
    let arr = [1i32, 2, 3, 4, 5];
    let ptr = &arr[0] as *const i32;

    unsafe {
        // Offset by 2
        let p2 = offset(ptr, 2isize);
        assert_eq!(*p2, 3);

        // Offset by 3
        let p3 = offset(ptr, 3isize);
        assert_eq!(*p3, 4);
    }
}

// Test offset to last element
fn test_offset_to_end() {
    let arr = [1i32, 2, 3, 4, 5];
    let ptr = &arr[0] as *const i32;

    unsafe {
        let p4 = offset(ptr, 4isize);
        assert_eq!(*p4, 5);
    }
}

// Test negative offset (moving backwards)
fn test_offset_negative() {
    let arr = [10i32, 20, 30, 40, 50];
    let ptr = &arr[3] as *const i32; // Start at element 3 (value 40)

    unsafe {
        // Move back 2 positions
        let p_back = offset(ptr, -2isize);
        assert_eq!(*p_back, 20);

        // Move back 1 position
        let p_back1 = offset(ptr, -1isize);
        assert_eq!(*p_back1, 30);

        // Stay at current position
        let p_same = offset(ptr, 0isize);
        assert_eq!(*p_same, 40);
    }
}
