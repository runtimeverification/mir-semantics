use std::time::Duration;

fn from_millis_check(ms: u64) {
    let d = Duration::from_millis(ms);
    assert!(d.as_secs() == ms / 1_000);
    assert!(d.subsec_millis() == (ms % 1_000) as u32);
}

fn main() {
    from_millis_check(0);
    from_millis_check(1000);
    from_millis_check(1500);
    from_millis_check(2999);
}
