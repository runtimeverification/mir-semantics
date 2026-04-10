use std::alloc::{Layout, alloc, handle_alloc_error};

#[no_mangle]
pub fn verify_box_from_raw(value: u32) {
    unsafe {
        let layout = Layout::new::<u32>();
        let ptr = alloc(layout).cast::<u32>();
        if ptr.is_null() {
            handle_alloc_error(layout);
        }

        ptr.write(value);
        let boxed = Box::from_raw(ptr);

        assert_eq!(*boxed, value);
    }
}

fn main() {}
