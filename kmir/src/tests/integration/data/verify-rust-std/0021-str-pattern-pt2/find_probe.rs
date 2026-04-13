// Probe: str::find with a &str pattern.
// Tests that "hello world".find("world") returns Some(6).

fn main() {
    let s = "hello world";
    let result = s.find("world");
    assert!(result.is_some());
    assert!(result.unwrap() == 6);
}
