use std::time::Duration;

fn test_checked_mul_basic() {
    let d = Duration::new(5, 0);
    let result = d.checked_mul(3).unwrap();
    assert!(result.as_secs() == 15);
    assert!(result.subsec_nanos() == 0);
}

fn test_checked_mul_with_nanos() {
    let d = Duration::new(1, 500_000_000);
    let result = d.checked_mul(2).unwrap();
    assert!(result.as_secs() == 3);
    assert!(result.subsec_nanos() == 0);
}

fn main() {
    test_checked_mul_basic();
    test_checked_mul_with_nanos();
}
