use std::cell::Cell;
use std::rc::Rc;

#[repr(C)]
struct RcInnerWitness<T> {
    strong: Cell<usize>,
    weak: Cell<usize>,
    value: T,
}

#[no_mangle]
pub fn verify_rc_deref() {
    let inner = std::pin::pin!(RcInnerWitness {
        strong: Cell::new(1),
        weak: Cell::new(1),
        value: 7u32,
    });
    let ptr = std::ptr::addr_of!(inner.as_ref().get_ref().value);
    let rc = unsafe { Rc::from_raw(ptr) };

    assert_eq!(*rc, 7);
    assert_eq!(Rc::strong_count(&rc), 1);
    assert_eq!(Rc::weak_count(&rc), 0);
    std::mem::forget(rc);
}

fn main() {}
