#![feature(allocator_api)]

use std::alloc::System;
use std::rc::Rc;

#[no_mangle]
pub fn verify_rc_from_raw_in(value: u32) {
    let rc = Rc::new_in(value, System);
    let ptr = Rc::into_raw(rc);
    let rc = unsafe { Rc::from_raw_in(ptr, System) };

    assert_eq!(*rc, value);
    assert_eq!(Rc::strong_count(&rc), 1);
    assert_eq!(Rc::weak_count(&rc), 0);
}

fn main() {}
