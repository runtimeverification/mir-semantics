use std::time::Duration;

fn test_checked_div_simple() {
    // Simple division that should produce an exact result
    let d = Duration::from_secs(15);
    let result = d.checked_div(3).unwrap();
    assert!(result.as_secs() == 5);
    assert!(result.subsec_nanos() == 0);
}

fn main() {
    test_checked_div_simple();
}
