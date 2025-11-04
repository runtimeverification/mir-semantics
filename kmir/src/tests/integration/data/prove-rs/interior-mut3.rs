use std::cell::UnsafeCell;

fn main() {
    let data = UnsafeCell::new(0);
    
    unsafe {
        *data.get() += 42;
    }
    
    assert!(data.into_inner() == 42)
}