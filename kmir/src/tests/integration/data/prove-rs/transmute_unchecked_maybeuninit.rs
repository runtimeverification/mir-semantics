#![feature(core_intrinsics)]
#![allow(deprecated)]

use std::intrinsics::transmute_unchecked;
use std::mem::MaybeUninit;

fn into_maybeuninit(value: i32) -> MaybeUninit<i32> {
    unsafe { transmute_unchecked::<i32, MaybeUninit<i32>>(value) }
}

fn from_maybeuninit(value: MaybeUninit<i32>) -> i32 {
    unsafe { transmute_unchecked::<MaybeUninit<i32>, i32>(value) }
}

fn main() {
    let maybe = into_maybeuninit(42);
    let roundtrip = from_maybeuninit(maybe);
    assert_eq!(roundtrip, 42);
}
