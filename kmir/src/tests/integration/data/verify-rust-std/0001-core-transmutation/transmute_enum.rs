//! Proof harnesses for transmute between integers and fieldless enums.
//! Tests the enum discriminant transmute rules.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

#[repr(u8)]
#[derive(PartialEq)]
enum Color {
    Red = 0,
    Green = 1,
    Blue = 2,
}

fn transmute_u8_to_color_red() {
    let c: Color = unsafe { transmute::<u8, Color>(0) };
    assert!(c == Color::Red);
}

fn transmute_u8_to_color_green() {
    let c: Color = unsafe { transmute::<u8, Color>(1) };
    assert!(c == Color::Green);
}

fn transmute_u8_to_color_blue() {
    let c: Color = unsafe { transmute::<u8, Color>(2) };
    assert!(c == Color::Blue);
}

#[repr(i32)]
#[derive(PartialEq)]
enum Status {
    Ok = 0,
    Error = -1,
    Pending = 1,
}

fn transmute_i32_to_status_ok() {
    let s: Status = unsafe { transmute::<i32, Status>(0) };
    assert!(s == Status::Ok);
}

fn transmute_i32_to_status_pending() {
    let s: Status = unsafe { transmute::<i32, Status>(1) };
    assert!(s == Status::Pending);
}

fn main() {
    transmute_u8_to_color_red();
    transmute_u8_to_color_green();
    transmute_u8_to_color_blue();
    transmute_i32_to_status_ok();
    transmute_i32_to_status_pending();
}
