#![feature(core_intrinsics)]
use std::intrinsics::{self, assert_inhabited};

fn main() {
    intrinsics::cold_path();
    let b = true;
    intrinsics::likely(b);
    intrinsics::unlikely(b);
    prefetch();
    assert_inhabited::<i32>(); // Up to compiler/CodegenBackend to panic or NOOP
    std::hint::black_box(
        assert_inhabited::<()>() // Trying to stop being optimised away
    );
}

fn prefetch() {
    let mut data = 11;
    let ptr = &data as *const i32;

    unsafe {
        intrinsics::prefetch_read_instruction::<i32>(ptr, 3);
        intrinsics::prefetch_read_data::<i32>(ptr, 3);
        assert_eq!(11, *ptr);
    }

    let ptr_mut = &mut data as *mut i32;
    unsafe {
        intrinsics::prefetch_write_instruction::<i32>(ptr_mut, 3);
        intrinsics::prefetch_write_data::<i32>(ptr_mut, 3);
        // (*ptr_mut) = 44;
        // assert_eq!(44, *ptr); // FIXME: fails due to thunks on casts
    }
}
