//! Proof harnesses for transmute_unchecked with struct and MaybeUninit<struct>.
//! Tests the transmute_unchecked path with non-primitive types.

#![feature(core_intrinsics)]
#![allow(deprecated)]

use std::intrinsics::transmute_unchecked;
use std::mem::MaybeUninit;

struct Pair {
    a: u32,
    b: u32,
}

fn transmute_unchecked_struct_into_maybeuninit() {
    let p = Pair { a: 10, b: 20 };
    let mu: MaybeUninit<Pair> = unsafe { transmute_unchecked::<Pair, MaybeUninit<Pair>>(p) };
    let p2 = unsafe { mu.assume_init() };
    assert!(p2.a == 10);
    assert!(p2.b == 20);
}

struct Something([u8; 3]);

fn transmute_unchecked_something() {
    let s = Something([1, 2, 3]);
    let mu: MaybeUninit<Something> = unsafe { transmute_unchecked::<Something, MaybeUninit<Something>>(s) };
    let s2 = unsafe { mu.assume_init() };
    assert!(s2.0[0] == 1);
    assert!(s2.0[1] == 2);
    assert!(s2.0[2] == 3);
}

fn main() {
    transmute_unchecked_struct_into_maybeuninit();
    transmute_unchecked_something();
}
