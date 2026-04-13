use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(true);

    let old = flag.fetch_xor(true, Ordering::SeqCst);

    assert!(old);
    assert!(!flag.load(Ordering::SeqCst));
}
