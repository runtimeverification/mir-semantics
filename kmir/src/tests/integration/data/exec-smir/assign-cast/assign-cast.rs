fn main() {

    // unsigned to signed
    let a: u16 = 33023 ; // 2^15 + (2^8 - 1);
    // narrowing
    let b = a as i8;     // -1
    // changing signedness
    let c = a as i16;    // -32513 = a - 2^16
    // widening
    let d = a as i32;    // 33023 == a

    // println!("a: {a}\nb: {b} = a as i8\nc: {c} = a as i16\nd: {d} = a as i32\n");

    // signed to signed
    // widening with sign
    let e = b as i16; // -1
    let f = d as i64; // 33023 == d
    // narrowing with sign
    let g = c as i8;  // -1
    let h = d as i8;  // -1 again

    // println!("e: {e} = -1 as i16\nf: {f} = d as i64\ng: {g} = c as i8\nh: {h} = d as i8\n");

    // signed to unsigned
    // changing signedness to unsigned
    let i = c as u16; // 33023 = a
    let j = d as u32; // 33023 = a
    // widening with sign
    let k = b as u16; // 65535!
    let l = d as u64; // 33023 = a
    // narrowing with sign
    let m = c as u8;  // 255 again
    let n = d as u8;  // 255 again

    // println!("i: {i} = c as u16\nj: {j} = d as u32\nk: {k} = b as u16\nl: {l} = d as u64\nm: {m} = c as u8\nn: {n} = d as u8\n");

    /* OUTPUT:
    a: 33023
    b: -1 = a as i8
    c: -32513 = a as i16
    d: 33023 = a as i32
    
    e: -1 = -1 as i16
    f: 33023 = d as i64
    g: -1 = c as i8
    h: -1 = d as i8
    
    i: 33023 = c as u16
    j: 33023 = d as u32
    k: 65535 = b as u16
    l: 33023 = d as u64
    m: 255 = c as u8
    n: 255 = d as u8
    */
}
