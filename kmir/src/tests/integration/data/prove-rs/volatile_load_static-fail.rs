#![feature(core_intrinsics)]
static A: i32 = 5555;

fn main() {
    let val: i32;
    unsafe {
        val = std::intrinsics::volatile_load(&A as *const i32);
    }

    assert!(val == 5555);
}
