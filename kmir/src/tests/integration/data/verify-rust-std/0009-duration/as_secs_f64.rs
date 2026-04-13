use std::time::Duration;

fn test_as_secs_f64_simple() {
    let d = Duration::from_secs(2);
    assert!(d.as_secs_f64() == 2.0_f64);
}

fn main() {
    test_as_secs_f64_simple();
}
