#![feature(f16)]
#![feature(f128)]

fn main() {
    // f16
    let a16: f16 = 3.5;
    assert!(-a16 == -3.5_f16);
    assert!(-(-a16) == a16);

    // f32
    let a32: f32 = 3.5;
    assert!(-a32 == -3.5_f32);
    assert!(-(-a32) == a32);

    // f64
    let a64: f64 = 3.5;
    assert!(-a64 == -3.5_f64);
    assert!(-(-a64) == a64);

    // f128
    let a128: f128 = 3.5;
    assert!(-a128 == -3.5_f128);
    assert!(-(-a128) == a128);

    // Negating zero
    assert!(-0.0_f16 == 0.0_f16);
    assert!(-0.0_f32 == 0.0_f32);
    assert!(-0.0_f64 == 0.0_f64);
    assert!(-0.0_f128 == 0.0_f128);
}
