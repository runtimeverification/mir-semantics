use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(false);

    assert!(!flag.load(Ordering::SeqCst));
}
