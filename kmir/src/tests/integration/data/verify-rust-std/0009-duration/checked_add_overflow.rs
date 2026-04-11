use std::time::Duration;

fn checked_add_overflow_secs() {
    // Maximum Duration + 1 second should overflow to None
    let d = Duration::new(u64::MAX, 999_999_999);
    let result = d.checked_add(Duration::from_secs(1));
    assert!(result.is_none());
}

fn checked_add_overflow_nanos() {
    // Maximum Duration + 1 nanosecond should overflow to None
    let d = Duration::new(u64::MAX, 999_999_999);
    let result = d.checked_add(Duration::from_nanos(1));
    assert!(result.is_none());
}

fn main() {
    checked_add_overflow_secs();
    checked_add_overflow_nanos();
}
