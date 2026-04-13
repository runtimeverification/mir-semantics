#![feature(step_trait)]

// Harness for `<char as Step>::forward_unchecked` (core::iter::range)
//
// Verifies that forward_unchecked correctly advances a char by a given count.

use std::iter::Step;

fn main() {
    // Advance 'A' by 1 -> 'B'
    let c1 = unsafe { char::forward_unchecked('A', 1) };
    assert!(c1 == 'B');

    // Advance 'A' by 0 -> 'A'
    let c2 = unsafe { char::forward_unchecked('A', 0) };
    assert!(c2 == 'A');

    // Advance '0' by 5 -> '5'
    let c3 = unsafe { char::forward_unchecked('0', 5) };
    assert!(c3 == '5');

    // Advance 'a' by 25 -> 'z'
    let c4 = unsafe { char::forward_unchecked('a', 25) };
    assert!(c4 == 'z');
}
