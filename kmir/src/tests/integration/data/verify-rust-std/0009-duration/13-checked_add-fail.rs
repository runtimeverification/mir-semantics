use std::time::Duration;

fn checked_add_wrong_assertion() {
    let a = Duration::new(5, 0);
    let b = Duration::new(3, 0);
    let result = a.checked_add(b).unwrap();
    // Intentionally wrong: claim result is 7 (should be 8)
    assert!(result.as_secs() == 7);
}

fn main() {
    checked_add_wrong_assertion();
}
