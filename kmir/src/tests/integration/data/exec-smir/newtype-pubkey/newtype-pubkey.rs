#![allow(dead_code)]

#[derive(Copy, Clone)]
pub struct Pubkey(pub [u8; 32]);

const KEY: Pubkey = Pubkey([
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
]);

#[inline(never)]
fn use_inner(arr: &[u8; 32]) -> usize {
    // Touch the array so MIR keeps the projection
    if arr[0] == 0 { 32 } else { 0 }
}

fn main() {
    let pk = KEY;           // forces constant decoding of StructType(newtype)
    let len = use_inner(&pk.0); // field projection .0; needs StructType decode to Aggregate
    core::hint::black_box(len);
}

