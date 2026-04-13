use std::time::Duration;

fn main() {
    assert!(Duration::ZERO.is_zero());
    assert!(!Duration::from_secs(1).is_zero());
}
