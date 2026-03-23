#![feature(core_intrinsics)]
use std::intrinsics::ptr_offset_from_unsigned; // core::ptr variant since 1.87.0, not for us

fn testing(mode: isize) {
    let a = [1, 2, 3, 4, 5];
    let b = [6, 7, 8, 9, 10];
    let a_p = &a as *const i32;
    let b_p = &b as *const i32;
    let a1: *const i32 = &a[1];
    let a3: *const i32 = &a[3];
    let b1: *const i32 = &b[1];

    match mode {
        0 => unsafe { // correct and expected operation on pointers with offset
            let a1_p = a_p.add(1);
            assert_eq!(a1_p.offset_from(a_p), 1);
            assert_eq!(a_p.offset_from(a1_p), -1);
            assert_eq!(ptr_offset_from_unsigned(a1_p, a_p), 1);
        },
        1 => unsafe { // correct and expected operation on addresses within arrays
            assert_eq!(a3.offset_from(a1), 2);
            assert_eq!(a1.offset_from(a3), -2);
        },
        2 => unsafe { // different allocation
            assert_eq!(a1.offset_from(b1), 0xdeadbeef); // UB
        },
        3 => unsafe {
            // violating assumption of a3 > a1
            assert_eq!(ptr_offset_from_unsigned(a1, a3), 0xdeadbeef); // UB
        },
        4 => unsafe {
            let unit_p: *const () = &();
            assert_eq!(unit_p.offset_from(unit_p), 0xdeadbeef); // panics
        },
        _ => ()
    }
}


fn main() {
    testing(0);
    testing(4);
}