#![feature(allocator_api)]

use std::alloc::System;
use std::rc::Rc;

fn main() {
    let rc = Rc::new_in(7u32, System);
    assert_eq!(*rc, 7);
}
