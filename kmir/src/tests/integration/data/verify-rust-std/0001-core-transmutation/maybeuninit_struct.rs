//! Proof harnesses for MaybeUninit with struct types.
//! Tests that MaybeUninit correctly wraps and unwraps struct values.

use std::mem::MaybeUninit;

struct Point {
    x: i32,
    y: i32,
}

fn test_maybeuninit_struct_point() {
    let p = Point { x: 10, y: 20 };
    let mu = MaybeUninit::new(p);
    let p2 = unsafe { mu.assume_init() };
    assert!(p2.x == 10);
    assert!(p2.y == 20);
}

struct Triple {
    a: u8,
    b: u16,
    c: u32,
}

fn test_maybeuninit_struct_triple() {
    let t = Triple { a: 1, b: 2, c: 3 };
    let mu = MaybeUninit::new(t);
    let t2 = unsafe { mu.assume_init() };
    assert!(t2.a == 1);
    assert!(t2.b == 2);
    assert!(t2.c == 3);
}

struct Wrapper(u64);

fn test_maybeuninit_wrapper() {
    let w = Wrapper(12345);
    let mu = MaybeUninit::new(w);
    let w2 = unsafe { mu.assume_init() };
    assert!(w2.0 == 12345);
}

fn main() {
    test_maybeuninit_struct_point();
    test_maybeuninit_struct_triple();
    test_maybeuninit_wrapper();
}
