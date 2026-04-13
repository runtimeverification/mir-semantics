use std::sync::atomic::{AtomicU32, Ordering};

fn main() {
    let value = AtomicU32::new(7);

    assert_eq!(value.load(Ordering::Relaxed), 7);

    value.store(11, Ordering::Relaxed);
    assert_eq!(value.load(Ordering::Relaxed), 11);

    let previous = value.fetch_add(5, Ordering::Relaxed);
    assert_eq!(previous, 11);
    assert_eq!(value.load(Ordering::Relaxed), 16);
}
