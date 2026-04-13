use std::cell::Cell;
use std::rc::Rc;

#[repr(C)]
struct RcInnerWitness<T> {
    strong: Cell<usize>,
    weak: Cell<usize>,
    value: T,
}

#[no_mangle]
pub fn verify_rc_clone_count() {
    let inner = std::pin::pin!(RcInnerWitness {
        strong: Cell::new(1),
        weak: Cell::new(1),
        value: 11u32,
    });
    let ptr = std::ptr::addr_of!(inner.as_ref().get_ref().value);
    let rc = unsafe { Rc::from_raw(ptr) };
    let rc_clone = Rc::clone(&rc);

    assert_eq!(*rc, 11);
    assert_eq!(*rc_clone, 11);
    assert_eq!(Rc::strong_count(&rc), 2);
    assert_eq!(Rc::strong_count(&rc_clone), 2);
    assert_eq!(Rc::weak_count(&rc), 0);
    std::mem::forget(rc_clone);
    std::mem::forget(rc);
}

fn main() {}
