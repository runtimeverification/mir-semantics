#![feature(repr_simd)]

#[repr(simd)]
#[derive(Clone, Copy)]
struct I32x2([i32; 2]);

fn main() {
    let v = I32x2([1_i32, 2_i32]);
    let I32x2(values) = v;
    assert!(values[0] == 1_i32);
    assert!(values[1] == 2_i32);
}
