//! Proof harnesses for MaybeUninit::new and assume_init on various integer types.
//! Tests the transmute bridge from T -> MaybeUninit<T> -> T.

use std::mem::MaybeUninit;

fn test_new_assume_init_nested() {
    let inner = MaybeUninit::new(42u32);
    let val = unsafe { inner.assume_init() };
    let outer = MaybeUninit::new(val + 1);
    let result = unsafe { outer.assume_init() };
    assert!(result == 43);
}

fn test_new_assume_init_i8() {
    let mu = MaybeUninit::new(-128i8);
    let val = unsafe { mu.assume_init() };
    assert!(val == -128);
}

fn test_new_assume_init_i16() {
    let mu = MaybeUninit::new(32767i16);
    let val = unsafe { mu.assume_init() };
    assert!(val == 32767);
}

fn test_new_assume_init_i32() {
    let mu = MaybeUninit::new(i32::MIN);
    let val = unsafe { mu.assume_init() };
    assert!(val == i32::MIN);
}

fn test_new_assume_init_u128() {
    let mu = MaybeUninit::new(999999u128);
    let val = unsafe { mu.assume_init() };
    assert!(val == 999999);
}

fn main() {
    test_new_assume_init_nested();
    test_new_assume_init_i8();
    test_new_assume_init_i16();
    test_new_assume_init_i32();
    test_new_assume_init_u128();
}
