use std::num::{NonZeroI8, NonZeroU8};

fn main() {
    part1_new_u8(1);
    part1_new_i8(1);
}

fn part1_new_u8(x: u8) {
    let result = NonZeroU8::new(x);
    if x == 0 {
        assert!(result.is_none());
    } else {
        assert!(result.is_some());
        assert!(result.unwrap().get() == x);
    }
}

fn part1_new_i8(x: i8) {
    let result = NonZeroI8::new(x);
    if x == 0 {
        assert!(result.is_none());
    } else {
        assert!(result.is_some());
        assert!(result.unwrap().get() == x);
    }
}
