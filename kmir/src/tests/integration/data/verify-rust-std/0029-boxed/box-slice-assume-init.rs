use std::alloc::{Layout, alloc, handle_alloc_error};
use std::mem::MaybeUninit;
use std::ptr;

#[no_mangle]
pub fn verify_box_slice_assume_init_u32_pair(first: u32, second: u32) {
    unsafe {
        let layout = Layout::array::<MaybeUninit<u32>>(2).expect("slice layout should be computable");
        let raw = alloc(layout).cast::<MaybeUninit<u32>>();
        if raw.is_null() {
            handle_alloc_error(layout);
        }

        raw.add(0).write(MaybeUninit::new(first));
        raw.add(1).write(MaybeUninit::new(second));

        let slice_ptr = ptr::slice_from_raw_parts_mut(raw, 2);
        let boxed = Box::<[MaybeUninit<u32>]>::from_raw(slice_ptr);
        let boxed = boxed.assume_init();

        assert_eq!(boxed.len(), 2);
        assert_eq!(boxed[0], first);
        assert_eq!(boxed[1], second);
    }
}

fn main() {}
