// Bitwise operations on symbolic values that the prover can only reason about after the bitwise lemmas in
// `bitwise-lemmas.md` turn them into arithmetic (`modInt`, `/Int`, `*Int`) that Z3 understands. Without them, each
// assertion splits into a branch where it fails.

/// A low mask is the remainder for nonnegative values. For negative values, `%` keeps the sign of `x` but the mask
/// does not, so a nonzero remainder is off by 256.
#[no_mangle]
pub fn mask_is_rem(x: i64) {
    let m = x & 0xFF;
    if x >= 0 {
        assert_eq!(m, x % 256);
    } else {
        let r = x % 256;
        assert_eq!(m, if r == 0 { 0 } else { r + 256 });
    }
}

/// A low mask is the same with the mask on either side.
#[no_mangle]
pub fn mask_comm(x: i64) {
    assert_eq!(0xFF & x, x & 0xFF);
}

/// A right shift is a division.
#[no_mangle]
pub fn shr_is_div(x: u64) {
    assert_eq!(x >> 8, x / 256);
}

/// Repeated right shifts are a single division.
#[no_mangle]
pub fn shr_shr_is_div(x: u64) {
    assert_eq!((x >> 1) >> 2, x / 8);
}

/// A left shift that does not overflow is a multiplication. `<<` drops the bits shifted out but `*` checks for overflow,
/// so the value is widened first.
#[no_mangle]
pub fn shl_is_mul(x: u32) {
    let y = x as u64;
    assert_eq!(y << 3, y * 8);
}

/// The first step of a parallel bit count: masking with 0x5555_5555 bounds both halves below 2^31, so their sum
/// cannot overflow.
#[no_mangle]
pub fn masked_sum_no_overflow(x: u32) -> u32 {
    (x & 0x5555_5555) + ((x >> 1) & 0x5555_5555)
}

/// The bitwise and with a nonnegative value lies between zero and that value.
#[no_mangle]
pub fn and_nonneg_bounds(x: i64, y: i64) {
    if x >= 0 {
        assert!(0 <= x & y);
        assert!(x & y >= 0);
        assert!(x & y <= x);
        assert!(x >= x & y);
    }
}

/// The bitwise or of two nonnegative values is nonnegative.
#[no_mangle]
pub fn or_nonneg(x: i64, y: i64) {
    if x >= 0 && y >= 0 {
        assert!(0 <= x | y);
    }
}

/// The bitwise or of two bytes is a byte.
#[no_mangle]
pub fn or_bytes_fit(a: u8, b: u8) {
    let (a, b) = (a as u16, b as u16);
    assert!(a | b < 256);
}

/// The bitwise or of two bytes is at most the largest byte.
#[no_mangle]
pub fn or_bytes_fit_le(a: u8, b: u8) {
    let (a, b) = (a as u16, b as u16);
    assert!(a | b <= 255);
}

/// A round trip through the native-endian bytes is a cast. Not a test of the bitwise lemmas, but of their interaction
/// with the existing round-trip lemmas.
#[no_mangle]
pub fn ne_bytes_roundtrip(x: i64) {
    assert_eq!(u64::from_ne_bytes(x.to_ne_bytes()), x as u64);
}

fn main() {
    mask_is_rem(-0x1234);
    mask_comm(-0x1234);
    shr_is_div(0x1234);
    shr_shr_is_div(0x1234);
    shl_is_mul(0x1234);
    masked_sum_no_overflow(0xFFFF_FFFF);
    and_nonneg_bounds(6, -3);
    or_nonneg(6, 3);
    or_bytes_fit(0x0F, 0xF0);
    or_bytes_fit_le(0x0F, 0xF0);
    ne_bytes_roundtrip(-2);
}
