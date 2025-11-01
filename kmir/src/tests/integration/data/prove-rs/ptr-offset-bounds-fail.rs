#![feature(core_intrinsics)]
use std::intrinsics::offset;

// This test should fail - offset beyond array bounds
fn main() {
    let arr = [1i32, 2, 3, 4, 5];
    let ptr = &arr[0] as *const i32;

    unsafe {
        // This should trigger UB - offsetting beyond the end
        let p_oob = offset(ptr, 6isize);
        let _x = *p_oob; // Accessing out of bounds
    }
}
