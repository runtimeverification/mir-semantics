#![feature(step_trait)]

// Harness for `<char as Step>::forward_checked` (core::iter::range)
//
// Verifies that forward_checked correctly advances a char by a given count,
// returning Some for valid results.

use std::iter::Step;

fn main() {
    // Advance 'A' by 1 -> Some('B')
    let c1 = char::forward_checked('A', 1);
    assert!(c1.is_some());
    assert!(c1.unwrap() == 'B');

    // Advance 'A' by 0 -> Some('A')
    let c2 = char::forward_checked('A', 0);
    assert!(c2.is_some());
    assert!(c2.unwrap() == 'A');

    // Advance '0' by 5 -> Some('5')
    let c3 = char::forward_checked('0', 5);
    assert!(c3.is_some());
    assert!(c3.unwrap() == '5');
}
