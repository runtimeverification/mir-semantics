/// Test that a stack pointer transmuted to usize is non-zero.
use std::mem::transmute;

fn main() {
    let x: u32 = 42;
    let ptr: *const u32 = &x;
    unsafe {
        let addr: usize = transmute(ptr);
        assert!(addr != 0);
    }
}
