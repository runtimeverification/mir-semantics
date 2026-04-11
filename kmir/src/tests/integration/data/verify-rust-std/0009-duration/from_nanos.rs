use std::time::Duration;

fn from_nanos_check(ns: u64, expected_secs: u64, expected_subsec_nanos: u32) {
    let d = Duration::from_nanos(ns);
    assert!(d.as_secs() == expected_secs);
    assert!(d.subsec_nanos() == expected_subsec_nanos);
}

fn main() {
    from_nanos_check(0, 0, 0);
    from_nanos_check(1_000_000_000, 1, 0);
    from_nanos_check(1_500_000_000, 1, 500_000_000);
    from_nanos_check(2_999_999_999, 2, 999_999_999);
}
