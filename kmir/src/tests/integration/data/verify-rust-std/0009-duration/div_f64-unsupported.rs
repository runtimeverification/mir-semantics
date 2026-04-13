use std::time::Duration;

fn test_div_f64_simple() {
    assert!(Duration::from_secs(10).div_f64(2.5) == Duration::from_secs(4));
}

fn main() {
    test_div_f64_simple();
}
