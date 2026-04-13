use std::ptr;

fn main() {
    let data = [3i32, 6i32, 9i32, 12i32, 15i32];
    let base = data.as_ptr();

    let value: i32;
    unsafe {
        value = ptr::read(base.add(3));
    }

    assert!(value == 12);
}
