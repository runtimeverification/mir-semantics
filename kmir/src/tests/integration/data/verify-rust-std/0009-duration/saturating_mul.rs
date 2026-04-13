use std::time::Duration;

fn test_saturating_mul_basic() {
    let d = Duration::new(5, 0);
    let result = d.saturating_mul(3);
    assert!(result.as_secs() == 15);
    assert!(result.subsec_nanos() == 0);
}

fn main() {
    test_saturating_mul_basic();
}
