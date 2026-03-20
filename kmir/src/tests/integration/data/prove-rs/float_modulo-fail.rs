#![feature(f16)]
#![feature(f128)]

fn main() {
    assert!(7.0_f16 % 4.0_f16 == 3.0_f16);
    assert!(7.0_f32 % 4.0_f32 == 3.0_f32);
    assert!(7.0_f64 % 4.0_f64 == 3.0_f64);
    assert!(7.0_f128 % 4.0_f128 == 3.0_f128);
}
