#![feature(core_io_borrowed_buf)]

// Harness for `BorrowedCursor::reborrow` (core::io::borrowed_buf)
//
// Verifies that reborrowing preserves the view over the unfilled region.

use std::io::BorrowedBuf;
use std::mem::MaybeUninit;

fn main() {
    let mut backing = [MaybeUninit::<u8>::uninit(); 8];
    let mut buf = BorrowedBuf::from(backing.as_mut_slice());
    let mut cursor = buf.unfilled();

    {
        let child = cursor.reborrow();
        assert!(child.capacity() == 8);
        assert!(child.written() == 0);
    }

    assert!(cursor.capacity() == 8);
    assert!(cursor.written() == 0);
}
