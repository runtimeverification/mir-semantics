use std::time::Duration;

fn test_checked_sub_nanos_borrow() {
    let result = Duration::new(5, 200_000_000)
        .checked_sub(Duration::new(2, 700_000_000))
        .unwrap();
    assert!(result == Duration::new(2, 500_000_000));
}

fn main() {
    test_checked_sub_nanos_borrow();
}
