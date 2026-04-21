#![feature(core_intrinsics)]
use std::mem::MaybeUninit;

fn main() {
    unsafe {
        let maybe_unsigned = std::intrinsics::transmute::<i128, MaybeUninit::<u128>>(9999);
                                  // Note different types ^^^^                ^^^^
        assert!(maybe_unsigned.assume_init() == 9999);
    }
}
