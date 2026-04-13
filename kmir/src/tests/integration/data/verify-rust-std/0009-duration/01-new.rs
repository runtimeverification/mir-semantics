use std::time::Duration;

fn main() {
    // Duration::new carries nanos >= 1_000_000_000 into seconds
    let d1 = Duration::new(5, 0);
    assert!(d1.as_secs() == 5);
    assert!(d1.subsec_nanos() == 0);

    let d2 = Duration::new(5, 500_000_000);
    assert!(d2.as_secs() == 5);
    assert!(d2.subsec_nanos() == 500_000_000);

    let d3 = Duration::new(0, 0);
    assert!(d3.as_secs() == 0);
    assert!(d3.subsec_nanos() == 0);

    let d4 = Duration::new(0, 999_999_999);
    assert!(d4.as_secs() == 0);
    assert!(d4.subsec_nanos() == 999_999_999);

    let d5 = Duration::new(0, 1_000_000_000);
    assert!(d5.as_secs() == 1);
    assert!(d5.subsec_nanos() == 0);

    let d6 = Duration::new(0, 1_500_000_000);
    assert!(d6.as_secs() == 1);
    assert!(d6.subsec_nanos() == 500_000_000);
}
