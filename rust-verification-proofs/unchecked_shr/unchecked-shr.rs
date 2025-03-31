#![feature(unchecked_shifts)]

fn main() {
    let a:i16 = 42;
    let b:u32 = 4;
    
    let result = unchecked_op(a, b);
}

fn unchecked_op(a: i16, b: u32) -> i16 {
    let unchecked_res = unsafe { a.unchecked_shr(b) };
    unchecked_res
}
