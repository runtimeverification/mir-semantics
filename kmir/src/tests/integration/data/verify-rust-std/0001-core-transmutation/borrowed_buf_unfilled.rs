#![feature(core_io_borrowed_buf)]

// Harness for `BorrowedBuf::unfilled` (core::io::borrowed_buf)
//
// Verifies that BorrowedBuf::unfilled returns a cursor over the unfilled part.

use std::io::BorrowedBuf;
use std::mem::MaybeUninit;

fn main() {
    let mut buf = [MaybeUninit::uninit(); 16];
    let mut bb = BorrowedBuf::from(buf.as_mut_slice());
    let cursor = bb.unfilled();
    assert!(cursor.capacity() == 16);
}
