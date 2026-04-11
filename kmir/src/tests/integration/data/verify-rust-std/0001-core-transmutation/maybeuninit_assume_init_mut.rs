//! Proof harnesses for MaybeUninit::assume_init_mut.
//! Tests reading the initialized value by mutable reference.

use std::mem::MaybeUninit;

fn test_assume_init_mut_read() {
    let mut mu = MaybeUninit::new(42u32);
    let val_ref: &mut u32 = unsafe { mu.assume_init_mut() };
    assert!(*val_ref == 42);
}

fn test_assume_init_mut_read_i64() {
    let mut mu = MaybeUninit::new(-50i64);
    let val_ref: &mut i64 = unsafe { mu.assume_init_mut() };
    assert!(*val_ref == -50);
}

fn main() {
    test_assume_init_mut_read();
    test_assume_init_mut_read_i64();
}
