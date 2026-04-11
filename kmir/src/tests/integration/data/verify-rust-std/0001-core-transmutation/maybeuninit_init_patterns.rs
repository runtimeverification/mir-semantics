//! Proof harnesses for various MaybeUninit initialization patterns.
//! Tests new -> assume_init chain with different types and patterns.

use std::mem::MaybeUninit;

fn test_option_some() {
    let mu = MaybeUninit::new(Some(42u32));
    let val = unsafe { mu.assume_init() };
    match val {
        Some(x) => assert!(x == 42),
        None => assert!(false),
    }
}

fn test_option_none() {
    let mu = MaybeUninit::new(None::<u32>);
    let val: Option<u32> = unsafe { mu.assume_init() };
    match val {
        Some(_) => assert!(false),
        None => {} // expected
    }
}

fn test_result_ok() {
    let mu = MaybeUninit::new(Ok::<u32, u32>(100));
    let val: Result<u32, u32> = unsafe { mu.assume_init() };
    match val {
        Ok(x) => assert!(x == 100),
        Err(_) => assert!(false),
    }
}

fn test_result_err() {
    let mu = MaybeUninit::new(Err::<u32, u32>(999));
    let val: Result<u32, u32> = unsafe { mu.assume_init() };
    match val {
        Ok(_) => assert!(false),
        Err(e) => assert!(e == 999),
    }
}

fn test_array_in_maybeuninit() {
    let arr = [1u32, 2, 3, 4, 5];
    let mu = MaybeUninit::new(arr);
    let arr2 = unsafe { mu.assume_init() };
    assert!(arr2[0] == 1);
    assert!(arr2[4] == 5);
}

fn main() {
    test_option_some();
    test_option_none();
    test_result_ok();
    test_result_err();
    test_array_in_maybeuninit();
}
