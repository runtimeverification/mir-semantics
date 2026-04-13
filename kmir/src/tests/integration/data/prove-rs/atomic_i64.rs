use std::sync::atomic::{AtomicI64, Ordering};

fn main() {
    let value = AtomicI64::new(-4);

    assert_eq!(value.load(Ordering::Relaxed), -4);

    let previous = value.fetch_sub(6, Ordering::Relaxed);
    assert_eq!(previous, -4);
    assert_eq!(value.load(Ordering::Relaxed), -10);
}
