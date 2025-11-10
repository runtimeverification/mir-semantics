#![feature(core_intrinsics)]
use std::intrinsics;

fn main() {
    intrinsics::cold_path();
    let b = true;
    intrinsics::likely(b);
    intrinsics::unlikely(b);
    prefetch();
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
