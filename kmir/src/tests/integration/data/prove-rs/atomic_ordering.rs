use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(false);

    assert!(!flag.load(Ordering::Relaxed));

    flag.store(true, Ordering::Release);
    assert!(flag.load(Ordering::Acquire));

    flag.store(false, Ordering::Release);
    assert!(!flag.load(Ordering::Relaxed));
}
