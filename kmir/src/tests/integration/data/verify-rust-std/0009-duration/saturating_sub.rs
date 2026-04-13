use std::time::Duration;

fn test_saturating_sub_basic() {
    let a = Duration::new(5, 0);
    let b = Duration::new(3, 0);
    let result = a.saturating_sub(b);
    assert!(result.as_secs() == 2);
    assert!(result.subsec_nanos() == 0);
}

fn test_saturating_sub_underflow_to_zero() {
    let a = Duration::new(3, 0);
    let b = Duration::new(5, 0);
    let result = a.saturating_sub(b);
    assert!(result.as_secs() == 0);
    assert!(result.subsec_nanos() == 0);
}

fn main() {
    test_saturating_sub_basic();
    test_saturating_sub_underflow_to_zero();
}
