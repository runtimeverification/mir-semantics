use std::time::Duration;

fn from_millis_check(ms: u64, expected_secs: u64, expected_subsec_millis: u32) {
    let d = Duration::from_millis(ms);
    assert!(d.as_secs() == expected_secs);
    assert!(d.subsec_millis() == expected_subsec_millis);
}

fn main() {
    from_millis_check(0, 0, 0);
    from_millis_check(1000, 1, 0);
    from_millis_check(1500, 1, 500);
    from_millis_check(2999, 2, 999);
}
