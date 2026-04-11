use std::time::Duration;

fn new_check(secs: u64, nanos: u32, expected_secs: u64, expected_nanos: u32) {
    let d = Duration::new(secs, nanos);
    assert!(d.as_secs() == expected_secs);
    assert!(d.subsec_nanos() == expected_nanos);
}

fn main() {
    new_check(5, 0, 5, 0);
    new_check(5, 500_000_000, 5, 500_000_000);
    new_check(0, 0, 0, 0);
    new_check(0, 999_999_999, 0, 999_999_999);
    // nanos >= 1_000_000_000 should carry over to seconds
    new_check(0, 1_000_000_000, 1, 0);
    new_check(0, 1_500_000_000, 1, 500_000_000);
}
