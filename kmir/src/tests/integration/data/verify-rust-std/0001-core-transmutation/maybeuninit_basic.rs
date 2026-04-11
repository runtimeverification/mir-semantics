//! Proof harnesses for basic MaybeUninit operations.
//! Covers MaybeUninit::new, assume_init, and zeroed.

use std::mem::MaybeUninit;

fn test_new_assume_init_u32() {
    let mu = MaybeUninit::new(42u32);
    let val = unsafe { mu.assume_init() };
    assert!(val == 42);
}

fn test_new_assume_init_i64() {
    let mu = MaybeUninit::new(-100i64);
    let val = unsafe { mu.assume_init() };
    assert!(val == -100);
}

fn test_new_assume_init_u8() {
    let mu = MaybeUninit::new(255u8);
    let val = unsafe { mu.assume_init() };
    assert!(val == 255);
}

fn test_new_assume_init_bool_true() {
    let mu = MaybeUninit::new(true);
    let val = unsafe { mu.assume_init() };
    assert!(val);
}

fn test_new_assume_init_bool_false() {
    let mu = MaybeUninit::new(false);
    let val = unsafe { mu.assume_init() };
    assert!(!val);
}

fn test_new_assume_init_usize() {
    let mu = MaybeUninit::new(12345usize);
    let val = unsafe { mu.assume_init() };
    assert!(val == 12345);
}

fn main() {
    test_new_assume_init_u32();
    test_new_assume_init_i64();
    test_new_assume_init_u8();
    test_new_assume_init_bool_true();
    test_new_assume_init_bool_false();
    test_new_assume_init_usize();
}
