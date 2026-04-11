use std::time::Duration;

fn checked_div_by_zero() {
    // Division by zero should return None
    let d = Duration::from_secs(15);
    let result = d.checked_div(0);
    assert!(result.is_none());
}

fn main() {
    checked_div_by_zero();
}
