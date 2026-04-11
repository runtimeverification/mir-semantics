//! Proof harnesses for MaybeUninit::assume_init_ref.
//! Tests reading the initialized value by reference.

use std::mem::MaybeUninit;

fn test_assume_init_ref_u32() {
    let mu = MaybeUninit::new(42u32);
    let val_ref: &u32 = unsafe { mu.assume_init_ref() };
    assert!(*val_ref == 42);
}

fn test_assume_init_ref_i64() {
    let mu = MaybeUninit::new(-100i64);
    let val_ref: &i64 = unsafe { mu.assume_init_ref() };
    assert!(*val_ref == -100);
}

fn test_assume_init_ref_u8() {
    let mu = MaybeUninit::new(200u8);
    let val_ref: &u8 = unsafe { mu.assume_init_ref() };
    assert!(*val_ref == 200);
}

fn main() {
    test_assume_init_ref_u32();
    test_assume_init_ref_i64();
    test_assume_init_ref_u8();
}
