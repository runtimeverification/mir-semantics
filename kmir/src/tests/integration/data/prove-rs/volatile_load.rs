#![feature(core_intrinsics)]
fn main() {
    let a: i32 = 5555;
    let a_ptr = &a as *const _;

    let b: i32;
    unsafe {
        b = std::intrinsics::volatile_load(a_ptr);
    }

    assert!(b == 5555);
}
