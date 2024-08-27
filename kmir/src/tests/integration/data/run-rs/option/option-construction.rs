#![allow(unused)]
fn main() {
    let a:Option<u32> = Some(42);
    let b:Option<u32> = None;
    let c:u32 = a.unwrap();
}