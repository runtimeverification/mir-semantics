#![feature(step_trait)]

// Harness for `<char as Step>::backward_unchecked` (core::iter::range)
//
// Verifies that backward_unchecked correctly retreats a char by a given count.

use std::iter::Step;

fn main() {
    // Retreat 'B' by 1 -> 'A'
    let c1 = unsafe { char::backward_unchecked('B', 1) };
    assert!(c1 == 'A');

    // Retreat 'z' by 25 -> 'a'
    let c2 = unsafe { char::backward_unchecked('z', 25) };
    assert!(c2 == 'a');

    // Retreat 'Z' by 0 -> 'Z'
    let c3 = unsafe { char::backward_unchecked('Z', 0) };
    assert!(c3 == 'Z');

    // Retreat '9' by 9 -> '0'
    let c4 = unsafe { char::backward_unchecked('9', 9) };
    assert!(c4 == '0');
}
