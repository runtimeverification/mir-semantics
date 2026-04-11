use std::time::Duration;

fn checked_sub_underflow_secs() {
    // Subtracting more seconds than available should produce None
    let d = Duration::from_secs(3);
    let result = d.checked_sub(Duration::from_secs(5));
    assert!(result.is_none());
}

fn checked_sub_underflow_zero() {
    // Subtracting 1 nanosecond from zero should produce None
    let d = Duration::from_secs(0);
    let result = d.checked_sub(Duration::from_nanos(1));
    assert!(result.is_none());
}

fn main() {
    checked_sub_underflow_secs();
    checked_sub_underflow_zero();
}
