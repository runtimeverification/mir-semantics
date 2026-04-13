use std::sync::atomic::{AtomicBool, Ordering};

fn main() {
    let flag = AtomicBool::new(false);

    let result = flag.compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst);

    assert_eq!(result, Ok(false));
    assert!(flag.load(Ordering::SeqCst));
}
