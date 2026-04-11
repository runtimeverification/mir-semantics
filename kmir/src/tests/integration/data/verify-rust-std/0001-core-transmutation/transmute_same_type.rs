//! Proof harnesses for transmute between identical types.
//! This is a degenerate but valid use of transmute.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

fn transmute_same_u32() {
    let x: u32 = 42;
    let y: u32 = unsafe { transmute::<u32, u32>(x) };
    assert!(x == y);
}

fn transmute_same_i64() {
    let x: i64 = -12345;
    let y: i64 = unsafe { transmute::<i64, i64>(x) };
    assert!(x == y);
}

fn transmute_same_u8() {
    let x: u8 = 255;
    let y: u8 = unsafe { transmute::<u8, u8>(x) };
    assert!(x == y);
}

fn transmute_same_usize() {
    let x: usize = 99999;
    let y: usize = unsafe { transmute::<usize, usize>(x) };
    assert!(x == y);
}

fn main() {
    transmute_same_u32();
    transmute_same_i64();
    transmute_same_u8();
    transmute_same_usize();
}
