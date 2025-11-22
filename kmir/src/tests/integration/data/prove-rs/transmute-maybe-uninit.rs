#![feature(core_intrinsics)]
use std::mem::MaybeUninit;

struct Something([u8; 3]);

fn main() {
    unsafe {
        let maybe_signed = std::intrinsics::transmute_unchecked::<i32, MaybeUninit::<i32>>(42);
        assert!(maybe_signed.assume_init() == 42);

        let maybe_unsigned = std::intrinsics::transmute::<u128, MaybeUninit::<u128>>(9999);
        assert!(maybe_unsigned.assume_init() == 9999);

        let something = Something([1, 2, 3]);
        let maybe_something = std::intrinsics::transmute::<Something, MaybeUninit::<Something>>(something);
        assert!(maybe_something.assume_init().0 == [1, 2, 3]);
    }
}
