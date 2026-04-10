use std::alloc::{Layout, alloc, handle_alloc_error};
use std::mem::MaybeUninit;

#[no_mangle]
pub fn verify_box_assume_init_u32(value: u32) {
    unsafe {
        let layout = Layout::new::<MaybeUninit<u32>>();
        let raw = alloc(layout).cast::<MaybeUninit<u32>>();
        if raw.is_null() {
            handle_alloc_error(layout);
        }

        raw.write(MaybeUninit::new(value));
        let boxed = Box::<MaybeUninit<u32>>::from_raw(raw);
        let boxed = boxed.assume_init();

        assert_eq!(*boxed, value);
    }
}

fn main() {}
