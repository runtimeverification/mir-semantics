#![feature(f16)]
#![feature(f128)]

fn main() {
    // f16
    assert!(1.0_f16 == 1.0_f16);
    assert!(0.0_f16 == 0.0_f16);
    assert!(1.0_f16 != 2.0_f16);

    // f32
    assert!(1.0_f32 == 1.0_f32);
    assert!(0.0_f32 == 0.0_f32);
    assert!(1.0_f32 != 2.0_f32);

    // f64
    assert!(1.0_f64 == 1.0_f64);
    assert!(0.0_f64 == 0.0_f64);
    assert!(1.0_f64 != 2.0_f64);

    // f128
    assert!(1.0_f128 == 1.0_f128);
    assert!(0.0_f128 == 0.0_f128);
    assert!(1.0_f128 != 2.0_f128);

    // Negative zero equals positive zero (IEEE 754)
    assert!(-0.0_f16 == 0.0_f16);
    assert!(-0.0_f32 == 0.0_f32);
    assert!(-0.0_f64 == 0.0_f64);
    assert!(-0.0_f128 == 0.0_f128);
}
