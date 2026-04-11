use std::time::Duration;

fn from_secs_wrong_assertion(secs: u64) {
    let d = Duration::from_secs(secs);
    // Intentionally wrong: claim subsec_nanos is 1 (should be 0)
    assert!(d.subsec_nanos() == 1);
}

fn main() {
    from_secs_wrong_assertion(42);
}
