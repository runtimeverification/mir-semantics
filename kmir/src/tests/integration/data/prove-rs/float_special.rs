#![feature(f16)]
#![feature(f128)]

fn main() {
    // f16 infinity
    let inf_16: f16 = 1.0_f16 / 0.0_f16;
    let neg_inf_16: f16 = -1.0_f16 / 0.0_f16;
    assert!(inf_16 == inf_16);
    assert!(neg_inf_16 == -inf_16);

    // f16 NaN
    let nan_16: f16 = 0.0_f16 / 0.0_f16;
    assert!(nan_16 != nan_16);
    assert!(!(nan_16 == nan_16));

    // f32 infinity
    let inf_32: f32 = 1.0_f32 / 0.0_f32;
    let neg_inf_32: f32 = -1.0_f32 / 0.0_f32;
    assert!(inf_32 == inf_32);
    assert!(inf_32 > 1.0e38_f32);
    assert!(neg_inf_32 < -1.0e38_f32);
    assert!(neg_inf_32 == -inf_32);

    // f32 NaN
    let nan_32: f32 = 0.0_f32 / 0.0_f32;
    assert!(nan_32 != nan_32);
    assert!(!(nan_32 == nan_32));
    assert!(!(nan_32 < 0.0_f32));
    assert!(!(nan_32 > 0.0_f32));

    // f64 infinity
    let inf_64: f64 = 1.0_f64 / 0.0_f64;
    let neg_inf_64: f64 = -1.0_f64 / 0.0_f64;
    assert!(inf_64 == inf_64);
    assert!(inf_64 > 1.0e308_f64);
    assert!(neg_inf_64 < -1.0e308_f64);
    assert!(neg_inf_64 == -inf_64);

    // f64 NaN
    let nan_64: f64 = 0.0_f64 / 0.0_f64;
    assert!(nan_64 != nan_64);
    assert!(!(nan_64 == nan_64));
    assert!(!(nan_64 < 0.0_f64));
    assert!(!(nan_64 > 0.0_f64));

    // f128 infinity
    let inf_128: f128 = 1.0_f128 / 0.0_f128;
    let neg_inf_128: f128 = -1.0_f128 / 0.0_f128;
    assert!(inf_128 == inf_128);
    assert!(neg_inf_128 == -inf_128);

    // f128 NaN
    let nan_128: f128 = 0.0_f128 / 0.0_f128;
    assert!(nan_128 != nan_128);
    assert!(!(nan_128 == nan_128));
}
