#![feature(non_zero_count_ones)]

use std::num::{NonZeroU16, NonZeroU8};

fn main() {
    part2_count_ones_u8(1);
    part2_count_ones_u16(1);
}

fn part2_count_ones_u8(x: u8) {
    if let Some(nz) = NonZeroU8::new(x) {
        let count = nz.count_ones();
        assert!(count.get() == x.count_ones());
        assert!(count.get() >= 1);
    }
}

fn part2_count_ones_u16(x: u16) {
    if let Some(nz) = NonZeroU16::new(x) {
        let count = nz.count_ones();
        assert!(count.get() == x.count_ones());
        assert!(count.get() >= 1);
    }
}
