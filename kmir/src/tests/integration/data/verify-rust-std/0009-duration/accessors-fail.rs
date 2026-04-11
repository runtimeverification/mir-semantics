use std::time::Duration;

fn accessors_wrong_assertion() {
    let d = Duration::new(5, 500_000_000);
    // Intentionally wrong: claim subsec_millis is 600 (should be 500)
    assert!(d.subsec_millis() == 600);
}

fn main() {
    accessors_wrong_assertion();
}
