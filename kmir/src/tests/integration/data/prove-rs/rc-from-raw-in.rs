#![feature(allocator_api)]

use std::boxed::Box;
use std::cell::Cell;
use std::alloc::System;
use std::rc::Rc;

#[repr(C)]
struct RcInnerWitness<T> {
    strong: Cell<usize>,
    weak: Cell<usize>,
    value: T,
}

fn main() {
    let inner = Box::new_in(
        RcInnerWitness { strong: Cell::new(1), weak: Cell::new(1), value: 7u32 },
        System,
    );
    let inner = Box::into_raw(inner);
    let ptr = unsafe { std::ptr::addr_of!((*inner).value) };

    // SAFETY: `ptr` points at the `value` field of a `repr(C)` witness that
    // matches `RcInner<T>` layout and was allocated with `System`.
    let rc = unsafe { Rc::from_raw_in(ptr, System) };

    assert_eq!(*rc, 7);
    assert_eq!(Rc::strong_count(&rc), 1);
}
