use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(false);

    let old = flag.swap(true, Ordering::SeqCst);

    assert!(!old);
    assert!(flag.load(Ordering::SeqCst));
}
