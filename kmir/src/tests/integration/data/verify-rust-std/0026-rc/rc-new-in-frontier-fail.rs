#![feature(allocator_api)]

use std::alloc::System;
use std::rc::Rc;

fn main() {
    let _ = Rc::new_in(7u32, System);
}
