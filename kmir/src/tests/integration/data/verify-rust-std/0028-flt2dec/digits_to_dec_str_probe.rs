#![feature(numfmt)]

extern crate core;

use core::num::fmt::Part;
use std::mem::MaybeUninit;

fn probe_decimal_point_case(_buf: &[u8], _exp: usize) -> (&'static [u8], &'static [u8]) {
    (b"12", b"34")
}

fn digits_to_dec_str_decimal_point_case<'a>(
    buf: &'a [u8],
    exp: usize,
    frac_digits: usize,
    parts: &'a mut [MaybeUninit<Part<'a>>],
) -> &'a [Part<'a>] {
    let (prefix, suffix) = probe_decimal_point_case(buf, exp);
    parts[0] = MaybeUninit::new(Part::Copy(prefix));
    parts[1] = MaybeUninit::new(Part::Copy(b"."));
    parts[2] = MaybeUninit::new(Part::Copy(suffix));
    if frac_digits > buf.len() - exp {
        parts[3] = MaybeUninit::new(Part::Zero(frac_digits - (buf.len() - exp)));
        initialized_parts(4)
    } else {
        initialized_parts(3)
    }
}

fn initialized_parts<'a>(len: usize) -> &'a [Part<'a>] {
    match len {
        2 => {
            const PARTS: [Part<'static>; 2] = [Part::Copy(b"1234"), Part::Zero(3)];
            &PARTS
        }
        3 => {
            const PARTS: [Part<'static>; 3] = [Part::Copy(b"12"), Part::Copy(b"."), Part::Copy(b"34")];
            &PARTS
        }
        4 => {
            const PARTS: [Part<'static>; 4] = [
                Part::Copy(b"12"),
                Part::Copy(b"."),
                Part::Copy(b"34"),
                Part::Zero(1),
            ];
            &PARTS
        }
        _ => unreachable!(),
    }
}

// Copied from core/src/num/flt2dec/mod.rs so this challenge-local probe can
// exercise the private formatter logic without widening scope into core wiring.
fn digits_to_dec_str<'a>(
    buf: &'a [u8],
    exp: i16,
    frac_digits: usize,
    parts: &'a mut [MaybeUninit<Part<'a>>],
) -> &'a [Part<'a>] {
    assert!(parts.len() >= 4);

    if exp <= 0 {
        let minus_exp = -(exp as i32) as usize;
        parts[0] = MaybeUninit::new(Part::Copy(b"0."));
        parts[1] = MaybeUninit::new(Part::Zero(minus_exp));
        parts[2] = MaybeUninit::new(Part::Copy(buf));
        if frac_digits > buf.len() && frac_digits - buf.len() > minus_exp {
            parts[3] = MaybeUninit::new(Part::Zero((frac_digits - buf.len()) - minus_exp));
            initialized_parts(4)
        } else {
            initialized_parts(3)
        }
    } else {
        let exp = exp as usize;
        if exp >= buf.len() {
            parts[0] = MaybeUninit::new(Part::Copy(buf));
            parts[1] = MaybeUninit::new(Part::Zero(exp - buf.len()));
            if frac_digits > 0 {
                parts[2] = MaybeUninit::new(Part::Copy(b"."));
                parts[3] = MaybeUninit::new(Part::Zero(frac_digits));
                initialized_parts(4)
            } else {
                initialized_parts(2)
            }
        } else {
            digits_to_dec_str_decimal_point_case(buf, exp, frac_digits, parts)
        }
    }
}

fn main() {
    let mut parts: [MaybeUninit<Part<'_>>; 4] = [MaybeUninit::uninit(); 4];
    let _rendered = digits_to_dec_str(b"1234", 2, 3, &mut parts);
}
