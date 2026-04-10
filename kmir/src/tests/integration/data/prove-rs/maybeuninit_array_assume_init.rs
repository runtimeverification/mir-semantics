#![feature(maybe_uninit_array_assume_init)]

use std::mem::MaybeUninit;

fn array_assume_init_u8(values: [MaybeUninit<u8>; 4]) -> [u8; 4] {
    unsafe { MaybeUninit::array_assume_init(values) }
}

fn array_assume_init_u16(values: [MaybeUninit<u16>; 2]) -> [u16; 2] {
    unsafe { MaybeUninit::array_assume_init(values) }
}

fn main() {
    let values_u8 = [
        MaybeUninit::new(1u8),
        MaybeUninit::new(2u8),
        MaybeUninit::new(3u8),
        MaybeUninit::new(4u8),
    ];
    assert_eq!(array_assume_init_u8(values_u8), [1, 2, 3, 4]);

    let values_u16 = [MaybeUninit::new(10u16), MaybeUninit::new(20u16)];
    assert_eq!(array_assume_init_u16(values_u16), [10, 20]);
}
