#![feature(c_str_literals)]
#![feature(clone_to_uninit)]

use std::clone::CloneToUninit;
use std::ffi::CStr;

macro_rules! precondition {
    ($cond:expr, $body:block) => {
        if $cond $body
    };
}

fn main() {
    test_clone_to_uninit_exact_bytes();
}

fn test_clone_to_uninit_exact_bytes() {
    let cstr = c"hello";
    let source_bytes = cstr.to_bytes_with_nul();
    let len = source_bytes.len();
    let mut dest = [0xAAu8; 6];
    let dest_ptr = dest.as_mut_ptr();

    precondition!(!dest_ptr.is_null(), {
        precondition!(len <= dest.len(), {
            unsafe {
                cstr.clone_to_uninit(dest_ptr);
            }

            let written = &dest[..len];

            assert!(written.len() == source_bytes.len());
            assert!(written[0] == source_bytes[0]);
            assert!(written[1] == source_bytes[1]);
            assert!(written[2] == source_bytes[2]);
            assert!(written[3] == source_bytes[3]);
            assert!(written[4] == source_bytes[4]);
            assert!(written[5] == source_bytes[5]);
            assert!(written[5] == 0);
            assert!(written == source_bytes);
        });
    });
}
