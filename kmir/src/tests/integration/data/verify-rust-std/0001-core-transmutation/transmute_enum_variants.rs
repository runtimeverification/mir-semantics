//! Proof harnesses for transmute between integers and fieldless enums.
//! Extended enum tests covering more discriminant patterns.

#![allow(clippy::unnecessary_transmute)]

use std::mem::transmute;

#[repr(u8)]
#[derive(PartialEq)]
enum Direction {
    North = 0,
    East = 1,
    South = 2,
    West = 3,
}

fn transmute_u8_to_all_directions() {
    let n: Direction = unsafe { transmute::<u8, Direction>(0) };
    let e: Direction = unsafe { transmute::<u8, Direction>(1) };
    let s: Direction = unsafe { transmute::<u8, Direction>(2) };
    let w: Direction = unsafe { transmute::<u8, Direction>(3) };
    assert!(n == Direction::North);
    assert!(e == Direction::East);
    assert!(s == Direction::South);
    assert!(w == Direction::West);
}

#[repr(u16)]
#[derive(PartialEq)]
enum Opcode {
    Nop = 0,
    Add = 1,
    Sub = 2,
    Mul = 3,
    Div = 4,
}

fn transmute_u16_to_opcodes() {
    let nop: Opcode = unsafe { transmute::<u16, Opcode>(0) };
    let add: Opcode = unsafe { transmute::<u16, Opcode>(1) };
    let div: Opcode = unsafe { transmute::<u16, Opcode>(4) };
    assert!(nop == Opcode::Nop);
    assert!(add == Opcode::Add);
    assert!(div == Opcode::Div);
}

#[repr(u8)]
#[derive(PartialEq)]
enum Bool {
    False = 0,
    True = 1,
}

fn transmute_u8_to_bool_enum() {
    let f: Bool = unsafe { transmute::<u8, Bool>(0) };
    let t: Bool = unsafe { transmute::<u8, Bool>(1) };
    assert!(f == Bool::False);
    assert!(t == Bool::True);
}

fn main() {
    transmute_u8_to_all_directions();
    transmute_u16_to_opcodes();
    transmute_u8_to_bool_enum();
}
