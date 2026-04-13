// Probe: Vec::from with an array.
// Tests that Vec::from([1, 2, 3]).len() == 3.

fn main() {
    let v = Vec::from([1, 2, 3]);
    assert!(v.len() == 3);
}
