use std::sync::atomic::{fence, Ordering};

fn main() {
    let mut value = 1;

    fence(Ordering::SeqCst);
    value += 1;

    assert_eq!(value, 2);
}
