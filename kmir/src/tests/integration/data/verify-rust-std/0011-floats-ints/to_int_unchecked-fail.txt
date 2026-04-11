#![feature(f16)]
#![feature(f128)]

fn main() {
    to_int_unchecked_f16_i8(0.0);
    to_int_unchecked_f32_i32(0.0);
    to_int_unchecked_f64_i64(0.0);
    to_int_unchecked_f128_i128(0.0);
}

fn to_int_unchecked_f16_i8(a: f16) {
    if a.is_finite() && a >= i8::MIN as f16 && a < -(i8::MIN as f16) {
        let result = unsafe { a.to_int_unchecked::<i8>() };
        assert!(result == a as i8);
    }
}

fn to_int_unchecked_f32_i32(a: f32) {
    if a.is_finite() && a >= i32::MIN as f32 && a < -(i32::MIN as f32) {
        let result = unsafe { a.to_int_unchecked::<i32>() };
        assert!(result == a as i32);
    }
}

fn to_int_unchecked_f64_i64(a: f64) {
    if a.is_finite() && a >= i64::MIN as f64 && a < -(i64::MIN as f64) {
        let result = unsafe { a.to_int_unchecked::<i64>() };
        assert!(result == a as i64);
    }
}

fn to_int_unchecked_f128_i128(a: f128) {
    if a.is_finite() && a >= i128::MIN as f128 && a < -(i128::MIN as f128) {
        let result = unsafe { a.to_int_unchecked::<i128>() };
        assert!(result == a as i128);
    }
}
