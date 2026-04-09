#![feature(nonzero_from_mut)]

use std::num::{NonZeroI8, NonZeroU8};

fn main() {
    part1_from_mut_u8(1);
    part1_from_mut_i8(1);
}

fn part1_from_mut_u8(mut x: u8) {
    let before = x;
    let result = NonZeroU8::from_mut(&mut x);

    if before == 0 {
        assert!(result.is_none());
        assert!(x == 0);
    } else {
        assert!(result.is_some());
        let nz_ref = result.unwrap();
        assert!(nz_ref.get() == before);
        *nz_ref = unsafe { NonZeroU8::new_unchecked(1) };
        assert!(x == 1);
    }
}

fn part1_from_mut_i8(mut x: i8) {
    let before = x;
    let result = NonZeroI8::from_mut(&mut x);

    if before == 0 {
        assert!(result.is_none());
        assert!(x == 0);
    } else {
        assert!(result.is_some());
        let nz_ref = result.unwrap();
        assert!(nz_ref.get() == before);
        let replacement = if before == 1 { -1 } else { 1 };
        *nz_ref = unsafe { NonZeroI8::new_unchecked(replacement) };
        assert!(x == replacement);
    }
}
