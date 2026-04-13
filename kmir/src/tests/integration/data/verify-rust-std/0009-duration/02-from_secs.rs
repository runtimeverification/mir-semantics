use std::time::Duration;

fn from_secs_roundtrip(secs: u64) {
    let d = Duration::from_secs(secs);
    assert!(d.as_secs() == secs);
    assert!(d.subsec_nanos() == 0);
}

fn main() {
    from_secs_roundtrip(0);
    from_secs_roundtrip(1);
    from_secs_roundtrip(42);
}
