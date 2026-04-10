#![feature(allocator_api, box_vec_non_null)]

use std::alloc::{Allocator, Layout, System};

#[no_mangle]
pub fn verify_box_from_non_null_in(value: u32) {
    unsafe {
        let non_null = System
            .allocate(Layout::new::<u32>())
            .expect("allocation for u32 should succeed")
            .cast::<u32>();

        non_null.as_ptr().write(value);
        let boxed = Box::from_non_null_in(non_null, System);

        assert_eq!(*boxed, value);
    }
}

fn main() {}
