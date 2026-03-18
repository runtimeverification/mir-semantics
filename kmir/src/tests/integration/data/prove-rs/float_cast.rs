#![feature(f16)]
#![feature(f128)]

fn main() {
    // FloatToInt
    assert!(3.14_f16 as i32 == 3);
    assert!(3.14_f32 as i32 == 3);
    assert!(3.14_f64 as i32 == 3);
    assert!(3.14_f128 as i32 == 3);

    // IntToFloat
    assert!(42_i64 as f16 == 42.0_f16);
    assert!(42_i64 as f32 == 42.0_f32);
    assert!(42_i64 as f64 == 42.0_f64);
    assert!(42_i64 as f128 == 42.0_f128);

    // FloatToFloat
    assert!(2.5_f32 as f64 == 2.5_f64);
    assert!(2.5_f64 as f32 == 2.5_f32);
    assert!(2.5_f16 as f64 == 2.5_f64);
    assert!(2.5_f64 as f128 == 2.5_f128);
}
