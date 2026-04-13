// Probe: str::chars iterator.
// Tests that "abc".chars().count() == 3.

fn main() {
    let s = "abc";
    let count = s.chars().count();
    assert!(count == 3);
}
