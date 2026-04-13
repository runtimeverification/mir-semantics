use std::time::Duration;

fn from_micros_check(us: u64) {
    let d = Duration::from_micros(us);
    assert!(d.as_secs() == us / 1_000_000);
    assert!(d.subsec_micros() == (us % 1_000_000) as u32);
}

fn main() {
    from_micros_check(0);
    from_micros_check(1_000_000);
    from_micros_check(1_500_000);
    from_micros_check(2_999_999);
}
