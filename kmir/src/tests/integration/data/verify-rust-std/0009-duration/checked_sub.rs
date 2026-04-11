use std::time::Duration;

fn test_checked_sub_basic() {
    let a = Duration::new(5, 0);
    let b = Duration::new(3, 0);
    let result = a.checked_sub(b).unwrap();
    assert!(result.as_secs() == 2);
    assert!(result.subsec_nanos() == 0);
}

fn test_checked_sub_with_nanos() {
    let a = Duration::new(5, 200_000_000);
    let b = Duration::new(2, 700_000_000);
    let result = a.checked_sub(b).unwrap();
    assert!(result.as_secs() == 2);
    assert!(result.subsec_nanos() == 500_000_000);
}

fn main() {
    test_checked_sub_basic();
    test_checked_sub_with_nanos();
}
