use std::num::{NonZeroI8, NonZeroU8};

fn main() {
    part1_new_unchecked_u8(1);
    part1_new_unchecked_i8(1);
}

fn part1_new_unchecked_u8(x: u8) {
    if x != 0 {
        let result = unsafe { NonZeroU8::new_unchecked(x) };
        assert!(result.get() == x);
    }
}

fn part1_new_unchecked_i8(x: i8) {
    if x != 0 {
        let result = unsafe { NonZeroI8::new_unchecked(x) };
        assert!(result.get() == x);
    }
}
