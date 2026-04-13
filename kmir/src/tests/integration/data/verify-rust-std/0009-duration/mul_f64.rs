use std::time::Duration;

fn main() {
    assert!(Duration::from_secs(2).mul_f64(1.5) == Duration::from_secs(3));
}
