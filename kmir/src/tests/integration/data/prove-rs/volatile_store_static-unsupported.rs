#![feature(core_intrinsics)]
static mut A: i32 = 5555;

fn main() {
    unsafe {
        std::intrinsics::volatile_store(&mut A as *mut i32, 7777);
    }

    unsafe {
        assert!(A == 7777);
    }
}
