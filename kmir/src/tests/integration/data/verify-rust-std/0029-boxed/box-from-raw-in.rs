#![feature(allocator_api)]

use std::alloc::{Allocator, Layout, System};

#[no_mangle]
pub fn verify_box_from_raw_in(value: u32) {
    unsafe {
        let ptr = System
            .allocate(Layout::new::<u32>())
            .expect("allocation for u32 should succeed")
            .cast::<u32>()
            .as_ptr();

        ptr.write(value);
        let boxed = Box::from_raw_in(ptr, System);

        assert_eq!(*boxed, value);
    }
}

fn main() {}
