#![feature(f16)]
#![feature(f128)]

fn main() {
    // f16
    assert!(1.5_f16 + 2.5_f16 == 4.0_f16);
    assert!(5.0_f16 - 1.5_f16 == 3.5_f16);
    assert!(2.0_f16 * 3.0_f16 == 6.0_f16);
    assert!(7.0_f16 / 2.0_f16 == 3.5_f16);

    // f32
    assert!(1.5_f32 + 2.5_f32 == 4.0_f32);
    assert!(5.0_f32 - 1.5_f32 == 3.5_f32);
    assert!(2.0_f32 * 3.0_f32 == 6.0_f32);
    assert!(7.0_f32 / 2.0_f32 == 3.5_f32);

    // f64
    assert!(3.5_f64 + 1.5_f64 == 5.0_f64);
    assert!(3.5_f64 - 1.5_f64 == 2.0_f64);
    assert!(3.5_f64 * 1.5_f64 == 5.25_f64);
    assert!(10.0_f64 / 2.0_f64 == 5.0_f64);

    // f128
    assert!(1.5_f128 + 2.5_f128 == 4.0_f128);
    assert!(5.0_f128 - 1.5_f128 == 3.5_f128);
    assert!(2.0_f128 * 3.0_f128 == 6.0_f128);
    assert!(7.0_f128 / 2.0_f128 == 3.5_f128);

    // Modulo (truncating)
    assert!(7.0_f16 % 4.0_f16 == 3.0_f16);
    assert!(7.0_f32 % 4.0_f32 == 3.0_f32);
    assert!(7.0_f64 % 4.0_f64 == 3.0_f64);
    assert!(7.0_f128 % 4.0_f128 == 3.0_f128);

    // Subnormal constant literals
    let sub_16: f16 = 5.96e-8_f16;       // below f16 min normal (6.1e-5)
    assert!(sub_16 + sub_16 == sub_16 * 2.0_f16);

    let sub_32: f32 = 1.0e-45_f32;       // below f32 min normal (1.2e-38)
    assert!(sub_32 + sub_32 == sub_32 * 2.0_f32);

    let sub_64: f64 = 5e-324_f64;        // below f64 min normal (2.2e-308)
    assert!(sub_64 + sub_64 == 1e-323_f64);

    let sub_128: f128 = 1.0e-4933_f128;  // below f128 min normal (~3.4e-4932)
    assert!(sub_128 + sub_128 == sub_128 * 2.0_f128);
}
