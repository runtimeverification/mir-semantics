#![feature(numfmt)]

extern crate core;

use core::num::fmt::Part;
use std::mem::MaybeUninit;

unsafe fn split_at_raw(buf: &[u8], mid: usize) -> (&[u8], &[u8]) {
    debug_assert!(mid <= buf.len());

    let ptr = buf.as_ptr();
    let prefix = std::slice::from_raw_parts(ptr, mid);
    let suffix = std::slice::from_raw_parts(ptr.add(mid), buf.len() - mid);
    (prefix, suffix)
}

// Copied from core/src/num/flt2dec/mod.rs so this challenge-local probe can
// exercise the private formatter logic without widening scope into core wiring.
fn digits_to_dec_str<'a>(
    buf: &'a [u8],
    exp: i16,
    frac_digits: usize,
    parts: &'a mut [MaybeUninit<Part<'a>>],
) -> &'a [Part<'a>] {
    assert!(!buf.is_empty());
    assert!(buf[0] > b'0');
    assert!(parts.len() >= 4);

    if exp <= 0 {
        let minus_exp = -(exp as i32) as usize;
        parts[0] = MaybeUninit::new(Part::Copy(b"0."));
        parts[1] = MaybeUninit::new(Part::Zero(minus_exp));
        parts[2] = MaybeUninit::new(Part::Copy(buf));
        if frac_digits > buf.len() && frac_digits - buf.len() > minus_exp {
            parts[3] = MaybeUninit::new(Part::Zero((frac_digits - buf.len()) - minus_exp));
            unsafe { std::slice::from_raw_parts(parts.as_ptr() as *const Part<'a>, 4) }
        } else {
            unsafe { std::slice::from_raw_parts(parts.as_ptr() as *const Part<'a>, 3) }
        }
    } else {
        let exp = exp as usize;
        if exp < buf.len() {
            let (prefix, suffix) = unsafe { split_at_raw(buf, exp) };
            parts[0] = MaybeUninit::new(Part::Copy(prefix));
            parts[1] = MaybeUninit::new(Part::Copy(b"."));
            parts[2] = MaybeUninit::new(Part::Copy(suffix));
            if frac_digits > buf.len() - exp {
                parts[3] = MaybeUninit::new(Part::Zero(frac_digits - (buf.len() - exp)));
                unsafe { std::slice::from_raw_parts(parts.as_ptr() as *const Part<'a>, 4) }
            } else {
                unsafe { std::slice::from_raw_parts(parts.as_ptr() as *const Part<'a>, 3) }
            }
        } else {
            parts[0] = MaybeUninit::new(Part::Copy(buf));
            parts[1] = MaybeUninit::new(Part::Zero(exp - buf.len()));
            if frac_digits > 0 {
                parts[2] = MaybeUninit::new(Part::Copy(b"."));
                parts[3] = MaybeUninit::new(Part::Zero(frac_digits));
                unsafe { std::slice::from_raw_parts(parts.as_ptr() as *const Part<'a>, 4) }
            } else {
                unsafe { std::slice::from_raw_parts(parts.as_ptr() as *const Part<'a>, 2) }
            }
        }
    }
}

fn main() {
    let mut parts: [MaybeUninit<Part<'_>>; 4] = [MaybeUninit::uninit(); 4];
    let rendered = digits_to_dec_str(b"1234", 2, 3, &mut parts);

    assert!(rendered.len() == 4);
}
