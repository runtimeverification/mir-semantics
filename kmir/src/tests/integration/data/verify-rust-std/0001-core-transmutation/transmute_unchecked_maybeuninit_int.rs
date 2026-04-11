//! Proof harnesses for transmute_unchecked from integer types INTO MaybeUninit.
//! Uses assume_init() to extract back (which is how std does it).

#![feature(core_intrinsics)]
#![allow(deprecated)]

use std::intrinsics::transmute_unchecked;
use std::mem::MaybeUninit;

fn transmute_unchecked_u32_into_maybeuninit() {
    let mu: MaybeUninit<u32> = unsafe { transmute_unchecked::<u32, MaybeUninit<u32>>(42) };
    let val = unsafe { mu.assume_init() };
    assert!(val == 42);
}

fn transmute_unchecked_u64_into_maybeuninit() {
    let mu: MaybeUninit<u64> = unsafe { transmute_unchecked::<u64, MaybeUninit<u64>>(0xDEADBEEF) };
    let val = unsafe { mu.assume_init() };
    assert!(val == 0xDEADBEEF);
}

fn transmute_unchecked_i32_into_maybeuninit() {
    let mu: MaybeUninit<i32> = unsafe { transmute_unchecked::<i32, MaybeUninit<i32>>(-100) };
    let val = unsafe { mu.assume_init() };
    assert!(val == -100);
}

fn transmute_unchecked_u8_into_maybeuninit() {
    let mu: MaybeUninit<u8> = unsafe { transmute_unchecked::<u8, MaybeUninit<u8>>(255) };
    let val = unsafe { mu.assume_init() };
    assert!(val == 255);
}

fn transmute_unchecked_u128_into_maybeuninit() {
    let mu: MaybeUninit<u128> = unsafe { transmute_unchecked::<u128, MaybeUninit<u128>>(9999) };
    let val = unsafe { mu.assume_init() };
    assert!(val == 9999);
}

fn main() {
    transmute_unchecked_u32_into_maybeuninit();
    transmute_unchecked_u64_into_maybeuninit();
    transmute_unchecked_i32_into_maybeuninit();
    transmute_unchecked_u8_into_maybeuninit();
    transmute_unchecked_u128_into_maybeuninit();
}
