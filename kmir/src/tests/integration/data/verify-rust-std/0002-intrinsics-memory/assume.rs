#![feature(core_intrinsics)]

fn main() {
    let x = 7_i32;

    unsafe { core::intrinsics::assume(x == 7); }

    assert!(x == 7);
}
