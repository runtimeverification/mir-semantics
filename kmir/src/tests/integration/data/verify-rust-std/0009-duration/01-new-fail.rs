use std::time::Duration;

fn new_wrong_assertion() {
    let d = Duration::new(5, 500_000_000);
    // Intentionally wrong: claim secs is 6 (should be 5)
    assert!(d.as_secs() == 6);
}

fn main() {
    new_wrong_assertion();
}
