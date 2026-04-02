/// Test that two different local pointers transmute to different addresses.
use std::mem::transmute;

fn main() {
    let a: u32 = 42;
    let b: u32 = 99;
    let pa: *const u32 = &a;
    let pb: *const u32 = &b;
    unsafe {
        let addr_a: usize = transmute(pa);
        let addr_b: usize = transmute(pb);
        assert!(addr_a != addr_b);
    }
}
