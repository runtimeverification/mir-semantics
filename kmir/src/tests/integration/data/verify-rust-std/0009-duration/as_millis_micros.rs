use std::time::Duration;

fn test_as_millis_and_as_micros() {
    let d = Duration::new(1, 500_000_000);
    assert!(d.as_millis() == 1500);
    assert!(d.as_micros() == 1_500_000);
}

fn main() {
    test_as_millis_and_as_micros();
}
