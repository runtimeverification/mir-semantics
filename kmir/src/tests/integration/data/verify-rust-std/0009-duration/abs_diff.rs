use std::time::Duration;

fn test_abs_diff_basic() {
    let a = Duration::new(5, 0);
    let b = Duration::new(3, 0);
    let result = a.abs_diff(b);
    assert!(result.as_secs() == 2);
    assert!(result.subsec_nanos() == 0);
}

fn test_abs_diff_with_nanos() {
    let a = Duration::new(5, 200_000_000);
    let b = Duration::new(2, 700_000_000);
    let result_ab = a.abs_diff(b);
    let result_ba = b.abs_diff(a);
    assert!(result_ab.as_secs() == 2);
    assert!(result_ab.subsec_nanos() == 500_000_000);
    assert!(result_ba.as_secs() == 2);
    assert!(result_ba.subsec_nanos() == 500_000_000);
}

fn main() {
    test_abs_diff_basic();
    test_abs_diff_with_nanos();
}
