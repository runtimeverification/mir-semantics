use std::time::Duration;

fn test_div_duration_f64_simple() {
    let lhs = Duration::from_secs(10);
    let rhs = Duration::from_secs(2);
    assert!(lhs.div_duration_f64(rhs) == 5.0_f64);
}

fn main() {
    test_div_duration_f64_simple();
}
