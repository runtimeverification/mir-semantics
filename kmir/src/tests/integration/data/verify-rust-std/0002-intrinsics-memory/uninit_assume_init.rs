extern crate core;

use core::mem::MaybeUninit;

fn main() {
    let mut value = MaybeUninit::<i32>::uninit();

    value.write(42_i32);

    let initialized = unsafe { value.assume_init() };

    assert!(initialized == 42_i32);
}
