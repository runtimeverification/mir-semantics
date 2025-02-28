fn main() {

    // unsigned to signed
    let a: u16 = 32896; // 2^15 + (2^7);
    // narrowing
    let b = a as i8;     // -128
    // changing signedness
    let c = a as i16;    // -32640 = a - 2^16
    // widening
    let d = a as i32;    // == a

    // println!("a: {a}\nb: {b} = a as i8\nc: {c} = a as i16\nd: {d} = a as i32\n");

    // signed to signed
    // widening with sign
    let e = b as i16; // -128
    let f = d as i64; // 32896 == d
    // narrowing with sign
    let g = c as i8;  // -128
    let h = d as i8;  // -128 again

    // println!("e: {e} = b as i16\nf: {f} = d as i64\ng: {g} = c as i8\nh: {h} = d as i8\n");

    // signed to unsigned
    // changing signedness to unsigned
    let i = c as u16; // == a
    let j = d as u32; // == a
    // widening with sign
    let k = b as u16; // 65408
    let l = d as u64; // == a
    // narrowing with sign
    let m = c as u8;  // 128
    let n = d as u8;  // 128
    let o = f as u32; // == a

    // println!("i: {i} = c as u16\nj: {j} = d as u32\nk: {k} = b as u16\nl: {l} = d as u64\nm: {m} = c as u8\nn: {n} = d as u8\no: {o} = f as u32\n");

    /* OUTPUT:
a: 32896
b: -128 = a as i8
c: -32640 = a as i16
d: 32896 = a as i32

e: -128 = b as i16
f: 32896 = d as i64
g: -128 = c as i8
h: -128 = d as i8

i: 32896 = c as u16
j: 32896 = d as u32
k: 65408 = b as u16
l: 32896 = d as u64
m: 128 = c as u8
n: 128 = d as u8
o: 32896 = f as u32
   */
}
