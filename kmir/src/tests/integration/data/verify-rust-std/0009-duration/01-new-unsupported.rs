use std::time::Duration;

fn new_check(secs: u64, nanos: u32) {
    let expected_secs = secs + (nanos / 1_000_000_000) as u64;
    let expected_nanos = nanos % 1_000_000_000;
    let d = Duration::new(secs, nanos);
    assert!(d.as_secs() == expected_secs);
    assert!(d.subsec_nanos() == expected_nanos);
}

fn main() {
    new_check(5, 0);
}
