use std::time::Duration;

fn from_nanos_check(ns: u64) {
    let d = Duration::from_nanos(ns);
    assert!(d.as_secs() == ns / 1_000_000_000);
    assert!(d.subsec_nanos() == (ns % 1_000_000_000) as u32);
}

fn main() {
    from_nanos_check(0);
    from_nanos_check(1_000_000_000);
    from_nanos_check(1_500_000_000);
    from_nanos_check(2_999_999_999);
}
