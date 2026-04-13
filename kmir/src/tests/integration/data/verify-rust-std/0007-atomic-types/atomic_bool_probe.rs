use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(true);
    assert!(flag.load(Ordering::SeqCst));
}
