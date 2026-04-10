#![feature(allocator_api)]

use std::alloc::System;
use std::sync::Arc;

#[no_mangle]
pub fn verify_arc_from_raw_in(value: u32) {
    let arc = Arc::new_in(value, System);
    let ptr = Arc::into_raw(arc);
    let arc = unsafe { Arc::from_raw_in(ptr, System) };

    assert_eq!(*arc, value);
    assert_eq!(Arc::strong_count(&arc), 1);
    assert_eq!(Arc::weak_count(&arc), 0);
}

fn main() {}
