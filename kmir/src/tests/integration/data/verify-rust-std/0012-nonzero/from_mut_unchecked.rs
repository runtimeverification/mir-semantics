#![feature(nonzero_from_mut)]

use std::num::NonZeroU8;

fn main() {
    part1_from_mut_unchecked_u8(1);
}

fn part1_from_mut_unchecked_u8(mut x: u8) {
    let before = x;
    let nz_ref = unsafe { NonZeroU8::from_mut_unchecked(&mut x) };

    assert!(nz_ref.get() == before);

    *nz_ref = unsafe { NonZeroU8::new_unchecked(2) };
    assert!(x == 2);
}
