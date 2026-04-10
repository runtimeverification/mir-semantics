#![feature(allocator_api)]

use std::alloc::System;
use std::sync::Arc;

fn main() {
    let arc = Arc::new_in(7u32, System);
    let ptr = Arc::into_raw(arc);
    let arc = unsafe { Arc::from_raw_in(ptr, System) };

    assert_eq!(*arc, 7);
    assert_eq!(Arc::strong_count(&arc), 1);
    assert_eq!(Arc::weak_count(&arc), 0);
}
