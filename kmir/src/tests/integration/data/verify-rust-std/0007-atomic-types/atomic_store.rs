use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(false);

    flag.store(true, Ordering::SeqCst);

    assert!(flag.load(Ordering::SeqCst));
}
