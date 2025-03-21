#![feature(unchecked_neg)]

fn main() {
    let a:i16 = 42;
    
    let result = unchecked_op(a);
}

fn unchecked_op(a: i16) -> i16 {
    let unchecked_res = unsafe { a.unchecked_neg() };
    unchecked_res
}
