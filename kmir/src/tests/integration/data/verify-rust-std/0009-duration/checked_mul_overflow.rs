use std::time::Duration;

fn checked_mul_overflow() {
    // Multiplying a large Duration by a large factor should overflow to None
    let d = Duration::from_secs(u64::MAX);
    let result = d.checked_mul(2);
    assert!(result.is_none());
}

fn checked_mul_overflow_nanos() {
    // Overflow through nanosecond accumulation
    let d = Duration::new(u64::MAX, 999_999_999);
    let result = d.checked_mul(2);
    assert!(result.is_none());
}

fn main() {
    checked_mul_overflow();
    checked_mul_overflow_nanos();
}
