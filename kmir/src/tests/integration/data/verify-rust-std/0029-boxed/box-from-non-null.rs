#![feature(box_vec_non_null)]

use std::alloc::{Layout, alloc, handle_alloc_error};
use std::ptr::NonNull;

#[no_mangle]
pub fn verify_box_from_non_null(value: u32) {
    unsafe {
        let layout = Layout::new::<u32>();
        let ptr = alloc(layout).cast::<u32>();
        if ptr.is_null() {
            handle_alloc_error(layout);
        }

        let non_null = NonNull::new_unchecked(ptr);
        non_null.as_ptr().write(value);
        let boxed = Box::from_non_null(non_null);

        assert_eq!(*boxed, value);
    }
}

fn main() {}
