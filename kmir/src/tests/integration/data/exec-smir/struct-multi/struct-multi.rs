#![allow(dead_code)]

#[derive(Copy, Clone)]
struct Pair([u8; 32], bool);

// Force a multi-field StructType constant so decoding happens at runtime
const P: Pair = Pair([
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
], true);

fn main() {
    // Use the constant so MIR emits a Constant->Allocated for a StructType with 2 fields
    let p = P;
    // Take a reference to the first field to trigger a field projection on a value
    // that is produced via constant decoding (which we haven't fully implemented for multi-field structs).
    let r = &p.0;
    core::hint::black_box(r);
}
