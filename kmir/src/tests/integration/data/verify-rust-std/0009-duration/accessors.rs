use std::time::Duration;

fn test_as_millis() {
    let d = Duration::new(5, 500_000_000);
    assert!(d.as_millis() == 5500);
}

fn test_as_micros() {
    let d = Duration::new(5, 500_000_000);
    assert!(d.as_micros() == 5_500_000);
}

fn test_as_nanos() {
    let d = Duration::new(5, 500_000_000);
    assert!(d.as_nanos() == 5_500_000_000);
}

fn test_subsec_millis() {
    let d = Duration::new(5, 500_000_000);
    assert!(d.subsec_millis() == 500);
}

fn test_subsec_micros() {
    let d = Duration::new(5, 500_000_000);
    assert!(d.subsec_micros() == 500_000);
}

fn test_subsec_nanos() {
    let d = Duration::new(5, 500_000_000);
    assert!(d.subsec_nanos() == 500_000_000);
}

fn main() {
    test_as_millis();
    test_as_micros();
    test_as_nanos();
    test_subsec_millis();
    test_subsec_micros();
    test_subsec_nanos();
}
