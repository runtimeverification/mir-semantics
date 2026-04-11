use std::time::Duration;

fn from_micros_check(us: u64, expected_secs: u64, expected_subsec_micros: u32) {
    let d = Duration::from_micros(us);
    assert!(d.as_secs() == expected_secs);
    assert!(d.subsec_micros() == expected_subsec_micros);
}

fn main() {
    from_micros_check(0, 0, 0);
    from_micros_check(1_000_000, 1, 0);
    from_micros_check(1_500_000, 1, 500_000);
    from_micros_check(2_999_999, 2, 999_999);
}
