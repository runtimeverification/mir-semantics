#![allow(dead_code)]

// Exercise decoding of a struct whose fields are not stored in declaration order.
// RangeInclusive<u8> is known to have such a layout on some platforms.

use std::ops::RangeInclusive;

// Force a multi-field StructType constant so decoding happens at runtime.
// Use RangeInclusive::new in a const context to avoid evaluation at run time.
const R: RangeInclusive<u8> = RangeInclusive::new(0, 31);

fn main() {
    // Use the constant so MIR emits a Constant->Allocated for a StructType with 2 fields
    let r = R;
    // Compute a boolean via public API that depends on correct internal layout decoding.
    // If decoding is wrong (e.g., ignoring non-ordered offsets), this expression can differ.
    let ok = r.contains(&0) && r.contains(&31) && !r.contains(&32);
    assert!(ok);
}
