use std::time::Duration;

fn test_saturating_add_basic() {
    let a = Duration::new(5, 0);
    let b = Duration::new(3, 0);
    let result = a.saturating_add(b);
    assert!(result.as_secs() == 8);
    assert!(result.subsec_nanos() == 0);
}

fn test_saturating_add_with_nanos() {
    let a = Duration::new(1, 500_000_000);
    let b = Duration::new(2, 700_000_000);
    let result = a.saturating_add(b);
    assert!(result.as_secs() == 4);
    assert!(result.subsec_nanos() == 200_000_000);
}

fn main() {
    test_saturating_add_basic();
    test_saturating_add_with_nanos();
}
