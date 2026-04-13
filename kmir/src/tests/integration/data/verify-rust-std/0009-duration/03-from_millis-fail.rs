use std::time::Duration;

fn from_millis_wrong_assertion() {
    let d = Duration::from_millis(1500);
    // Intentionally wrong: claim secs is 2 (should be 1)
    assert!(d.as_secs() == 2);
}

fn main() {
    from_millis_wrong_assertion();
}
