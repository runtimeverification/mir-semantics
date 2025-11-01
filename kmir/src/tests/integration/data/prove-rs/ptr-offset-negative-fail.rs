#![feature(core_intrinsics)]
use std::intrinsics::offset;

// This test should fail - negative offset before array start
fn main() {
    let arr = [1i32, 2, 3, 4, 5];
    let ptr = &arr[2] as *const i32; // Start at element 2 (value 3)

    unsafe {
        // This should trigger UB - offsetting before the start
        let p_oob = offset(ptr, -3isize); // Would go to index -1
        let _x = *p_oob; // Accessing before array start
    }
}
