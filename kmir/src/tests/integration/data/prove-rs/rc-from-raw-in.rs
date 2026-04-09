#![feature(allocator_api)]

use std::alloc::System;
use std::rc::Rc;

fn main() {
    let rc = Rc::new_in(7u32, System);
    let ptr = Rc::into_raw(rc);

    // SAFETY: `ptr` was just produced by `Rc::into_raw` from the same allocator.
    let rc = unsafe { Rc::from_raw_in(ptr, System) };

    assert_eq!(*rc, 7);
    assert_eq!(Rc::strong_count(&rc), 1);
}
